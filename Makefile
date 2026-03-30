.DEFAULT_GOAL := run

# ── What you usually want ─────────────────────────────────────────────
run:                ## Chat in the terminal (runs setup first if needed)
	@bash yoak.sh

ui:                 ## Web app: API + dashboard (open http://127.0.0.1:8420)
	@bash yoak.sh ui

talk:               ## Chat with your cofounder in the terminal
	@bash yoak.sh talk

setup:              ## Configure name, model, and paths
	@bash yoak.sh setup

notes:              ## Show your learning journal
	@bash yoak.sh notes

bmc:                ## Print your Business Model Canvas
	@bash yoak.sh bmc

# ── Older names (same commands) ───────────────────────────────────────
chat: talk
serve: ui
init: setup
journal: notes
canvas: bmc

help:               ## List Make targets
	@echo "Yoak — common commands:"
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) | awk -F ':.*## ' '{printf "  make %-10s %s\n", $$1, $$2}'
	@echo ""
	@echo "Aliases: chat=talk, serve=ui, init=setup, journal=notes, canvas=bmc"

.PHONY: run ui talk setup notes bmc chat serve init journal canvas help
