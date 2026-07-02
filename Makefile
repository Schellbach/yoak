.DEFAULT_GOAL := run

run:                ## Start Yoak (installs everything on first run)
	@bash yoak.sh $(ARGS)

chat:               ## Chat with your cofounder
	@bash yoak.sh chat

serve:              ## Start the web dashboard
	@bash yoak.sh serve

init:               ## Reconfigure model, project name
	@bash yoak.sh init

canvas:             ## Print your Lean Canvas
	@bash yoak.sh canvas

hypotheses:         ## List Lean Canvas hypotheses
	@bash yoak.sh hypotheses

journal:            ## Show your learning journal
	@bash yoak.sh journal

export:             ## Export memory to an Obsidian vault
	@bash yoak.sh export $(ARGS)

help:               ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) | awk -F ':.*## ' '{printf "  make %-12s %s\n", $$1, $$2}'

.PHONY: run chat serve init canvas hypotheses journal export help
