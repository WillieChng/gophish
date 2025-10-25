package api

import (
	"encoding/json"
	"net/http"

	"github.com/gorilla/mux"
	ctx "github.com/gophish/gophish/context"
	log "github.com/gophish/gophish/logger"
	"github.com/gophish/gophish/models"
)

// Scenarios returns a list of scenarios available to the user
func (as *Server) Scenarios(w http.ResponseWriter, r *http.Request) {
	switch {
	case r.Method == "GET":
		ss, err := models.GetScenarioSummaries(ctx.Get(r, "user_id").(int64))
		if err != nil {
			log.Error(err)
			JSONResponse(w, models.Response{Success: false, Message: "Error retrieving scenarios"}, http.StatusInternalServerError)
			return
		}
		JSONResponse(w, ss, http.StatusOK)
	case r.Method == "POST":
		s := models.Scenario{}
		err := json.NewDecoder(r.Body).Decode(&s)
		if err != nil {
			JSONResponse(w, models.Response{Success: false, Message: "Invalid JSON structure"}, http.StatusBadRequest)
			return
		}
		err = models.PostScenario(&s, ctx.Get(r, "user_id").(int64))
		if err != nil {
			JSONResponse(w, models.Response{Success: false, Message: err.Error()}, http.StatusBadRequest)
			return
		}
		JSONResponse(w, s, http.StatusCreated)
	}
}

// Scenario returns details about a specific scenario
func (as *Server) Scenario(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	id := vars["id"]

	switch {
	case r.Method == "GET":
		s, err := models.GetScenario(id, ctx.Get(r, "user_id").(int64))
		if err != nil {
			JSONResponse(w, models.Response{Success: false, Message: "Scenario not found"}, http.StatusNotFound)
			return
		}
		JSONResponse(w, s, http.StatusOK)
	case r.Method == "PUT":
		s := models.Scenario{}
		err := json.NewDecoder(r.Body).Decode(&s)
		if err != nil {
			JSONResponse(w, models.Response{Success: false, Message: "Invalid JSON structure"}, http.StatusBadRequest)
			return
		}
		err = models.PutScenario(&s, ctx.Get(r, "user_id").(int64))
		if err != nil {
			JSONResponse(w, models.Response{Success: false, Message: err.Error()}, http.StatusBadRequest)
			return
		}
		JSONResponse(w, s, http.StatusOK)
	case r.Method == "DELETE":
		err := models.DeleteScenario(id, ctx.Get(r, "user_id").(int64))
		if err != nil {
			if err == models.ErrCannotDeleteSystemScenario {
				JSONResponse(w, models.Response{Success: false, Message: "Cannot delete system scenarios"}, http.StatusForbidden)
				return
			}
			JSONResponse(w, models.Response{Success: false, Message: "Error deleting scenario"}, http.StatusInternalServerError)
			return
		}
		JSONResponse(w, models.Response{Success: true, Message: "Scenario deleted successfully"}, http.StatusOK)
	}
}
