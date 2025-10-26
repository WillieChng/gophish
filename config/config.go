package config

import (
	"bufio"
	"encoding/json"
	"os"
	"path/filepath"
	"strings"

	log "github.com/gophish/gophish/logger"
)

// AdminServer represents the Admin server configuration details
type AdminServer struct {
	ListenURL            string   `json:"listen_url"`
	UseTLS               bool     `json:"use_tls"`
	CertPath             string   `json:"cert_path"`
	KeyPath              string   `json:"key_path"`
	CSRFKey              string   `json:"csrf_key"`
	AllowedInternalHosts []string `json:"allowed_internal_hosts"`
	TrustedOrigins       []string `json:"trusted_origins"`
}

// PhishServer represents the Phish server configuration details
type PhishServer struct {
	ListenURL string `json:"listen_url"`
	UseTLS    bool   `json:"use_tls"`
	CertPath  string `json:"cert_path"`
	KeyPath   string `json:"key_path"`
}

// Config represents the configuration information.
type Config struct {
	AdminConf      AdminServer `json:"admin_server"`
	PhishConf      PhishServer `json:"phish_server"`
	DBName         string      `json:"db_name"`
	DBPath         string      `json:"db_path"`
	DBSSLCaPath    string      `json:"db_sslca_path"`
	MigrationsPath string      `json:"migrations_prefix"`
	TestFlag       bool        `json:"test_flag"`
	ContactAddress string      `json:"contact_address"`
	Logging        *log.Config `json:"logging"`
	MongoURI       string      `json:"mongo_uri"`
	MongoDB        string      `json:"mongo_db"`
}

// Version contains the current gophish version
var Version = ""

// ServerName is the server type that is returned in the transparency response.
const ServerName = "gophish"

// loadEnvFile loads environment variables from a .env file
// This allows us to share the .env file with the Python service
func loadEnvFile(envPath string) error {
	file, err := os.Open(envPath)
	if err != nil {
		// .env file is optional, not an error if it doesn't exist
		return nil
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())

		// Skip empty lines and comments
		if line == "" || strings.HasPrefix(line, "#") {
			continue
		}

		// Parse KEY=VALUE format
		parts := strings.SplitN(line, "=", 2)
		if len(parts) != 2 {
			continue
		}

		key := strings.TrimSpace(parts[0])
		value := strings.TrimSpace(parts[1])

		// Only set if not already set in environment
		if os.Getenv(key) == "" {
			os.Setenv(key, value)
		}
	}

	return scanner.Err()
}

// LoadConfig loads the configuration from the specified filepath
func LoadConfig(configPath string) (*Config, error) {
	// Try to load .env file from Phishing-Content-Generation-System directory
	// This allows sharing credentials between Go and Python services
	envPath := filepath.Join(filepath.Dir(configPath), "Phishing-Content-Generation-System", ".env")
	log.Infof("Attempting to load .env file from: %s", envPath)
	if err := loadEnvFile(envPath); err != nil {
		log.Warnf("Error loading .env file from %s: %v", envPath, err)
	} else {
		log.Infof("Successfully loaded .env file from: %s", envPath)
	}

	// Get the config file
	configFile, err := os.ReadFile(configPath)
	if err != nil {
		return nil, err
	}
	config := &Config{}
	err = json.Unmarshal(configFile, config)
	if err != nil {
		return nil, err
	}
	if config.Logging == nil {
		config.Logging = &log.Config{}
	}

	// Override MongoDB URI from environment variable if set (for security)
	if envMongoURI := os.Getenv("MONGO_URI"); envMongoURI != "" {
		log.Infof("BEFORE Override - config.MongoURI: %s", config.MongoURI)
		config.MongoURI = envMongoURI
		log.Infof("AFTER Override - Using MongoDB URI from environment: %s...", envMongoURI[:20])
	} else {
		log.Warnf("No MONGO_URI environment variable found, using config.json value: %s", config.MongoURI)
	}

	// Override MongoDB database name from environment variable if set
	if envMongoDB := os.Getenv("MONGO_DB"); envMongoDB != "" {
		config.MongoDB = envMongoDB
		log.Infof("Using MongoDB database from MONGO_DB environment variable: %s", envMongoDB)
	}

	// Choosing the migrations directory based on the database used.
	config.MigrationsPath = config.MigrationsPath + config.DBName
	// Explicitly set the TestFlag to false to prevent config.json overrides
	config.TestFlag = false
	return config, nil
}
