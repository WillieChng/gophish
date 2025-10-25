package models

import (
	"context"
	"time"

	log "github.com/gophish/gophish/logger"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

var mongoClient *mongo.Client
var mongoDB *mongo.Database

// SetupMongoDB initializes the MongoDB connection
func SetupMongoDB(uri, dbName string) error {
	if uri == "" {
		log.Info("MongoDB URI not configured, skipping MongoDB setup")
		return nil
	}

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	clientOptions := options.Client().ApplyURI(uri)
	client, err := mongo.Connect(ctx, clientOptions)
	if err != nil {
		log.Errorf("Failed to connect to MongoDB: %v", err)
		return err
	}

	// Ping the database to verify connection
	err = client.Ping(ctx, nil)
	if err != nil {
		log.Errorf("Failed to ping MongoDB: %v", err)
		return err
	}

	mongoClient = client
	mongoDB = client.Database(dbName)
	log.Infof("Successfully connected to MongoDB database: %s", dbName)
	return nil
}

// GetMongoDB returns the MongoDB database instance
func GetMongoDB() *mongo.Database {
	return mongoDB
}

// CloseMongoDB closes the MongoDB connection
func CloseMongoDB() error {
	if mongoClient == nil {
		return nil
	}
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	return mongoClient.Disconnect(ctx)
}
