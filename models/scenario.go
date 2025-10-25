package models

import (
	"context"
	"errors"
	"time"

	log "github.com/gophish/gophish/logger"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

// Scenario represents a phishing scenario template
type Scenario struct {
	ID              primitive.ObjectID `bson:"_id,omitempty" json:"id"`
	Name            string             `bson:"name" json:"name"`
	DisplayName     string             `bson:"display_name" json:"display_name"`
	Description     string             `bson:"description" json:"description"`
	IsSystem        bool               `bson:"is_system" json:"is_system"`
	OrganizationID  *int64             `bson:"organization_id,omitempty" json:"organization_id,omitempty"`
	CreatedByUserID *int64             `bson:"created_by_user_id,omitempty" json:"created_by_user_id,omitempty"`
	CreatedAt       time.Time          `bson:"created_at" json:"created_at"`
	UpdatedAt       time.Time          `bson:"updated_at" json:"updated_at"`
}

// ScenarioSummary is a lightweight version for listing
type ScenarioSummary struct {
	ID          primitive.ObjectID `json:"id"`
	Name        string             `json:"name"`
	DisplayName string             `json:"display_name"`
	Description string             `json:"description"`
	IsSystem    bool               `json:"is_system"`
}

// ErrScenarioNameNotSpecified is thrown when a scenario name is not specified
var ErrScenarioNameNotSpecified = errors.New("Scenario name not specified")

// ErrScenarioDisplayNameNotSpecified is thrown when a display name is not specified
var ErrScenarioDisplayNameNotSpecified = errors.New("Scenario display name not specified")

// ErrScenarioNotFound is thrown when a scenario is not found
var ErrScenarioNotFound = errors.New("Scenario not found")

// ErrCannotDeleteSystemScenario is thrown when trying to delete a system scenario
var ErrCannotDeleteSystemScenario = errors.New("Cannot delete system scenarios")

// Validate checks the scenario for required fields
func (s *Scenario) Validate() error {
	if s.Name == "" {
		return ErrScenarioNameNotSpecified
	}
	if s.DisplayName == "" {
		return ErrScenarioDisplayNameNotSpecified
	}
	return nil
}

// GetScenarios returns all scenarios available to the user
func GetScenarios(uid int64) ([]Scenario, error) {
	if mongoDB == nil {
		return []Scenario{}, errors.New("MongoDB not initialized")
	}

	collection := mongoDB.Collection("scenarios")
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	// Get system scenarios and user's custom scenarios
	// Filter: is_system=true OR created_by_user_id=uid
	filter := bson.M{
		"$or": []bson.M{
			{"is_system": true},
			{"created_by_user_id": uid},
		},
	}

	cursor, err := collection.Find(ctx, filter)
	if err != nil {
		log.Error(err)
		return nil, err
	}
	defer cursor.Close(ctx)

	var scenarios []Scenario
	if err = cursor.All(ctx, &scenarios); err != nil {
		log.Error(err)
		return nil, err
	}

	return scenarios, nil
}

// GetScenarioSummaries returns lightweight scenario summaries
func GetScenarioSummaries(uid int64) ([]ScenarioSummary, error) {
	scenarios, err := GetScenarios(uid)
	if err != nil {
		return nil, err
	}

	summaries := make([]ScenarioSummary, len(scenarios))
	for i, s := range scenarios {
		summaries[i] = ScenarioSummary{
			ID:          s.ID,
			Name:        s.Name,
			DisplayName: s.DisplayName,
			Description: s.Description,
			IsSystem:    s.IsSystem,
		}
	}
	return summaries, nil
}

// GetScenario returns a specific scenario by ID
func GetScenario(id string, uid int64) (Scenario, error) {
	if mongoDB == nil {
		return Scenario{}, errors.New("MongoDB not initialized")
	}

	objectID, err := primitive.ObjectIDFromHex(id)
	if err != nil {
		return Scenario{}, err
	}

	collection := mongoDB.Collection("scenarios")
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	var scenario Scenario
	err = collection.FindOne(ctx, bson.M{"_id": objectID}).Decode(&scenario)
	if err == mongo.ErrNoDocuments {
		return Scenario{}, ErrScenarioNotFound
	}
	if err != nil {
		log.Error(err)
		return Scenario{}, err
	}

	return scenario, nil
}

// GetScenarioByName returns a specific scenario by name
func GetScenarioByName(name string) (Scenario, error) {
	if mongoDB == nil {
		return Scenario{}, errors.New("MongoDB not initialized")
	}

	collection := mongoDB.Collection("scenarios")
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	var scenario Scenario
	err := collection.FindOne(ctx, bson.M{"name": name}).Decode(&scenario)
	if err == mongo.ErrNoDocuments {
		return Scenario{}, ErrScenarioNotFound
	}
	if err != nil {
		log.Error(err)
		return Scenario{}, err
	}

	return scenario, nil
}

// PostScenario creates a new scenario
func PostScenario(s *Scenario, uid int64) error {
	if err := s.Validate(); err != nil {
		return err
	}

	if mongoDB == nil {
		return errors.New("MongoDB not initialized")
	}

	// Check if scenario name already exists
	_, err := GetScenarioByName(s.Name)
	if err == nil {
		return errors.New("Scenario with this name already exists")
	}

	collection := mongoDB.Collection("scenarios")
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	s.CreatedAt = time.Now()
	s.UpdatedAt = time.Now()
	s.CreatedByUserID = &uid
	s.IsSystem = false // User-created scenarios are never system scenarios

	result, err := collection.InsertOne(ctx, s)
	if err != nil {
		log.Error(err)
		return err
	}

	s.ID = result.InsertedID.(primitive.ObjectID)
	return nil
}

// PutScenario updates an existing scenario
func PutScenario(s *Scenario, uid int64) error {
	if err := s.Validate(); err != nil {
		return err
	}

	if mongoDB == nil {
		return errors.New("MongoDB not initialized")
	}

	// Check if it's a system scenario
	existing, err := GetScenario(s.ID.Hex(), uid)
	if err != nil {
		return err
	}

	if existing.IsSystem {
		return errors.New("Cannot modify system scenarios")
	}

	collection := mongoDB.Collection("scenarios")
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	s.UpdatedAt = time.Now()
	s.CreatedAt = existing.CreatedAt // Preserve original creation time
	s.IsSystem = false                // Can't change to system

	filter := bson.M{"_id": s.ID}
	update := bson.M{"$set": s}

	_, err = collection.UpdateOne(ctx, filter, update)
	if err != nil {
		log.Error(err)
		return err
	}

	return nil
}

// DeleteScenario deletes a scenario by ID
func DeleteScenario(id string, uid int64) error {
	if mongoDB == nil {
		return errors.New("MongoDB not initialized")
	}

	// Check if it's a system scenario
	scenario, err := GetScenario(id, uid)
	if err != nil {
		return err
	}

	if scenario.IsSystem {
		return ErrCannotDeleteSystemScenario
	}

	objectID, err := primitive.ObjectIDFromHex(id)
	if err != nil {
		return err
	}

	collection := mongoDB.Collection("scenarios")
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	result, err := collection.DeleteOne(ctx, bson.M{"_id": objectID})
	if err != nil {
		log.Error(err)
		return err
	}

	if result.DeletedCount == 0 {
		return ErrScenarioNotFound
	}

	return nil
}

// SeedSystemScenarios seeds the database with default system scenarios
func SeedSystemScenarios() error {
	if mongoDB == nil {
		log.Info("MongoDB not initialized, skipping scenario seeding")
		return nil
	}

	collection := mongoDB.Collection("scenarios")
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	// Check if scenarios already exist
	count, err := collection.CountDocuments(ctx, bson.M{"is_system": true})
	if err != nil {
		return err
	}

	if count > 0 {
		log.Infof("System scenarios already exist (%d found), skipping seed", count)
		return nil
	}

	log.Info("Seeding system scenarios...")

	now := time.Now()
	systemScenarios := []interface{}{
		Scenario{
			Name:        "password_reset",
			DisplayName: "Password Reset",
			Description: "Simulates a password reset phishing attempt with urgency and suspicious links",
			IsSystem:    true,
			CreatedAt:   now,
			UpdatedAt:   now,
		},
		Scenario{
			Name:        "urgent_action",
			DisplayName: "Urgent Action Required",
			Description: "High-pressure phishing email demanding immediate action",
			IsSystem:    true,
			CreatedAt:   now,
			UpdatedAt:   now,
		},
		Scenario{
			Name:        "account_verification",
			DisplayName: "Account Verification",
			Description: "Requests account verification with suspicious links and urgency",
			IsSystem:    true,
			CreatedAt:   now,
			UpdatedAt:   now,
		},
		Scenario{
			Name:        "security_alert",
			DisplayName: "Security Alert",
			Description: "Fake security alert from IT department or security team",
			IsSystem:    true,
			CreatedAt:   now,
			UpdatedAt:   now,
		},
		Scenario{
			Name:        "document_share",
			DisplayName: "Document Share",
			Description: "Simulates a shared document or file with suspicious links",
			IsSystem:    true,
			CreatedAt:   now,
			UpdatedAt:   now,
		},
		Scenario{
			Name:        "invoice",
			DisplayName: "Invoice Payment",
			Description: "Fake invoice or payment request with attachments",
			IsSystem:    true,
			CreatedAt:   now,
			UpdatedAt:   now,
		},
		Scenario{
			Name:        "it_support",
			DisplayName: "IT Support Request",
			Description: "Fake IT support ticket or system maintenance notification",
			IsSystem:    true,
			CreatedAt:   now,
			UpdatedAt:   now,
		},
		Scenario{
			Name:        "hr_announcement",
			DisplayName: "HR Announcement",
			Description: "Fake HR announcement or policy update",
			IsSystem:    true,
			CreatedAt:   now,
			UpdatedAt:   now,
		},
	}

	// Create index on name field
	indexModel := mongo.IndexModel{
		Keys:    bson.D{{Key: "name", Value: 1}},
		Options: options.Index().SetUnique(true),
	}
	_, err = collection.Indexes().CreateOne(ctx, indexModel)
	if err != nil {
		log.Warnf("Failed to create index: %v", err)
	}

	// Insert scenarios
	result, err := collection.InsertMany(ctx, systemScenarios)
	if err != nil {
		log.Error(err)
		return err
	}

	log.Infof("Successfully seeded %d system scenarios", len(result.InsertedIDs))
	return nil
}
