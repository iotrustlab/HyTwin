.PHONY: demo test proofs

demo:
	python3 -m hytwin demo --output results/demo

test:
	bash check_all.sh

proofs:
	bash scripts/check_models.sh --prove
