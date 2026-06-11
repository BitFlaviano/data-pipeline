#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.pipeline.orchestrator import PipelineOrchestrator
from src.utils.logger import PipelineLogger


def parse_args():
    parser = argparse.ArgumentParser(
        description="Pipeline de Dados - ETL Genérico",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python run_pipeline.py
  python run_pipeline.py --config config/config.yaml
  python run_pipeline.py --output-json
  python run_pipeline.py --schedule daily
        """,
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config/config.yaml",
        help="Caminho para o arquivo de configuração YAML",
    )
    parser.add_argument(
        "--output-json",
        action="store_true",
        help="Exporta relatório da execução em JSON",
    )
    parser.add_argument(
        "--schedule",
        type=str,
        choices=["daily", "hourly", "weekly"],
        help="Agenda execução recorrente do pipeline",
    )
    return parser.parse_args()


def run_scheduled(pipeline, interval: str):
    import schedule
    import time

    interval_map = {
        "daily": schedule.every().day,
        "hourly": schedule.every().hour,
        "weekly": schedule.every().week,
    }

    interval_map[interval].do(pipeline.run)

    logger = PipelineLogger.get_logger_for_module("pipeline")
    logger.info(f"Pipeline agendado para execução {interval}")
    logger.info("Pressione Ctrl+C para parar")

    while True:
        schedule.run_pending()
        time.sleep(60)


def main():
    args = parse_args()
    logger = PipelineLogger.get_logger_for_module("pipeline")

    pipeline = PipelineOrchestrator(config_path=args.config)

    if args.schedule:
        run_scheduled(pipeline, args.schedule)
        return

    context = pipeline.run()

    print("\n" + "=" * 50)
    print("RESUMO DA EXECUÇÃO")
    print("=" * 50)
    print(f"Pipeline:       {context.pipeline_name}")
    print(f"Status:         {context.stage}")
    print(f"Duração:        {context.duration_seconds:.2f}s")
    print(f"Extraídos:      {context.extracted_rows}")
    print(f"Transformados:  {context.transformed_rows}")
    print(f"Carregados:     {context.loaded_rows}")
    print(f"Quality:        {context.quality_status}")
    print(f"Etapas:         {', '.join(context.steps_completed)}")
    if context.errors:
        print(f"Erros:          {len(context.errors)}")
        for err in context.errors:
            print(f"  - {err}")

    if args.output_json:
        output_path = Path("logs/last_run.json")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(context.to_dict(), f, indent=2, ensure_ascii=False)
        print(f"\nRelatório salvo em: {output_path}")

    sys.exit(0 if context.stage == "completed" else 1)


if __name__ == "__main__":
    main()
