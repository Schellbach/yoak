.DEFAULT_GOAL := run

run:                ## Start Yoak (installs everything on first run)
	@bash yoak.sh $(ARGS)

chat:               ## Chat with your cofounder
	@bash yoak.sh chat

serve:              ## Start the web dashboard
	@bash yoak.sh serve

init:               ## Reconfigure model, project name
	@bash yoak.sh init

canvas:             ## Print your Business Model Canvas
	@bash yoak.sh canvas

journal:            ## Show your learning journal
	@bash yoak.sh journal

help:               ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) | awk -F ':.*## ' '{printf "  make %-12s %s\n", $$1, $$2}'

.PHONY: run chat serve init canvas journal help
