package api

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"os/exec"
	"time"

	log "github.com/gophish/gophish/logger"
	"github.com/gophish/gophish/models"
)

// AITemplateRequest represents the request structure for AI template generation
type AITemplateRequest struct {
	Scenario           string `json:"scenario"`
	TargetCompany      string `json:"target_company"`
	IncludeLandingPage bool   `json:"include_landing_page"`
}

// AITemplateResponse represents the response from the Python AI module
type AITemplateResponse struct {
	Subject     string `json:"subject"`
	HTML        string `json:"html"`
	Text        string `json:"text"`
	LandingPage string `json:"landing_page,omitempty"`
}

// GenerateAITemplate handles POST requests to generate phishing templates using AI
func (as *Server) GenerateAITemplate(w http.ResponseWriter, r *http.Request) {
	switch r.Method {
	case "POST":
		// Parse the request
		var req AITemplateRequest
		err := json.NewDecoder(r.Body).Decode(&req)
		if err != nil {
			JSONResponse(w, models.Response{Success: false, Message: "Invalid JSON structure"}, http.StatusBadRequest)
			return
		}

		// Validate inputs
		if req.Scenario == "" {
			JSONResponse(w, models.Response{Success: false, Message: "Scenario is required"}, http.StatusBadRequest)
			return
		}
		if req.TargetCompany == "" {
			req.TargetCompany = "Your Organization" // Default value
		}

		// Call Python module to generate template
		template, err := generateTemplateWithAI(req.Scenario, req.TargetCompany, req.IncludeLandingPage)
		if err != nil {
			log.Errorf("Error generating AI template: %v", err)
			JSONResponse(w, models.Response{Success: false, Message: fmt.Sprintf("Failed to generate template: %v", err)}, http.StatusInternalServerError)
			return
		}

		// Return the generated template
		JSONResponse(w, template, http.StatusOK)

	default:
		JSONResponse(w, models.Response{Success: false, Message: "Method not allowed"}, http.StatusMethodNotAllowed)
	}
}

// generateTemplateWithAI calls the Python AI module to generate a phishing template
func generateTemplateWithAI(scenario string, targetCompany string, includeLandingPage bool) (*AITemplateResponse, error) {
	// Create context with timeout (30 seconds for AI generation)
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	// Build command to call Python module
	args := []string{
		"ai_module/generate_phishing.py",
		"--scenario", scenario,
		"--target", targetCompany,
		"--format", "json",
	}

	// Add landing page flag if requested
	if includeLandingPage {
		args = append(args, "--include-landing-page")
	}

	cmd := exec.CommandContext(ctx, "python", args...)

	// Capture output
	var stdout, stderr bytes.Buffer
	cmd.Stdout = &stdout
	cmd.Stderr = &stderr

	// Execute command
	err := cmd.Run()

	// Log output for debugging
	log.Infof("Python stdout: %s", stdout.String())
	if stderr.Len() > 0 {
		log.Infof("Python stderr: %s", stderr.String())
	}

	// Try to parse JSON response even if there was an error
	// (Python script may return error details in JSON format)
	var response AITemplateResponse
	parseErr := json.Unmarshal(stdout.Bytes(), &response)

	if parseErr != nil {
		// Could not parse JSON at all
		if err != nil {
			log.Errorf("Python script error: %v", err)
			log.Errorf("Stderr: %s", stderr.String())
			return nil, fmt.Errorf("AI module execution failed: %v - %s", err, stderr.String())
		}
		log.Errorf("Failed to parse AI response: %v", parseErr)
		log.Errorf("Output: %s", stdout.String())
		return nil, fmt.Errorf("failed to parse AI response: %v", parseErr)
	}

	// Check if the response contains an error field
	if response.Subject == "AI Generation Failed" || response.Subject == "Error: API Key Not Set" || response.Subject == "Error: Configuration File Missing" || response.Subject == "Error: AI Module Not Configured" {
		return nil, fmt.Errorf(response.Text)
	}

	return &response, nil
}
