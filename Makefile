.PHONY: help setup-user setup-dev data train eval pack test test-slow lint format bench clean

help:
	@echo "clarify-prompt make hedefleri:"
	@echo "  setup-user   Kullanici (inference) bagimliliklarini kur"
	@echo "  setup-dev    Kullanici + gelistirme (test, lint) bagimliliklari"
	@echo "  data         Egitim veri setini olustur (training/data/build.py)"
	@echo "  train        SFT egitimini calistir (varsayilan Qwen 2.5 7B config)"
	@echo "  eval         Test seti + judge ile degerlendir"
	@echo "  pack         LoRA'yi merge et, GGUF'ye cevir"
	@echo "  test         Birim testleri"
	@echo "  test-slow    Entegrasyon testleri (yavas, gercek llama-cli ister)"
	@echo "  lint         ruff + mypy"
	@echo "  format       ruff format"
	@echo "  bench        Gecikme + bellek olcumleri"
	@echo "  clean        Cache ve olusmus dosyalari temizle"

setup-user:
	pip install -e .

setup-dev:
	pip install -e ".[dev]"

data:
	python -m training.data.build

train:
	python -m training.sft.train --config training/configs/qwen2.5-7b-r16.yaml

eval:
	python -m training.eval.run --model training/outputs/latest

pack:
	python -m training.pack.merge_lora --adapter training/outputs/latest
	python -m training.pack.convert_to_gguf --model training/outputs/merged --quant Q4_K_M

test:
	pytest tests/unit -v

test-slow:
	pytest tests -v -m slow

lint:
	ruff check src tests training
	mypy src

format:
	ruff format src tests training

bench:
	python bench/latency.py
	python bench/memory.py

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage build dist *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
