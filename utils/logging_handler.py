"""
Logging Documentation System
로깅 기록을 구조화하여 문서화하는 시스템

Features:
- Structured logging to files
- API call tracking and documentation
- Error documentation
- Performance metrics
- Daily/weekly reports
- JSON and Markdown export
"""

import logging
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from collections import defaultdict
import traceback


class LogDocumenter:
    """
    로깅 기록을 문서화하는 클래스

    Features:
    - API 호출 추적 및 문서화
    - 에러 로그 분류 및 문서화
    - 성능 메트릭스 수집
    - 일일/주간 리포트 생성
    - JSON 및 Markdown 형식 지원
    """

    def __init__(
        self,
        log_dir: str = "logs/documented",
        enable_file_logging: bool = True,
        enable_console_logging: bool = True
    ):
        """
        LogDocumenter 초기화

        Args:
            log_dir: 로그 파일이 저장될 디렉토리
            enable_file_logging: 파일 로깅 활성화 여부
            enable_console_logging: 콘솔 로깅 활성화 여부
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Separate directories for different log types
        self.api_calls_dir = self.log_dir / "api_calls"
        self.errors_dir = self.log_dir / "errors"
        self.performance_dir = self.log_dir / "performance"
        self.reports_dir = self.log_dir / "reports"

        for directory in [self.api_calls_dir, self.errors_dir, self.performance_dir, self.reports_dir]:
            directory.mkdir(parents=True, exist_ok=True)

        self.enable_file_logging = enable_file_logging
        self.enable_console_logging = enable_console_logging

        # In-memory storage for report generation
        self.api_call_log: List[Dict[str, Any]] = []
        self.error_log: List[Dict[str, Any]] = []
        self.performance_log: List[Dict[str, Any]] = []

        # Setup logger
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """로거를 설정합니다."""
        logger = logging.getLogger('LogDocumenter')
        logger.setLevel(logging.DEBUG)

        # Clear existing handlers
        logger.handlers = []

        # Console handler
        if self.enable_console_logging:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        # File handler
        if self.enable_file_logging:
            log_file = self.log_dir / f"log_documenter_{datetime.now().strftime('%Y%m%d')}.log"
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        return logger

    def document_api_call(
        self,
        operation: str,
        parameters: Dict[str, Any],
        result: Optional[Dict[str, Any]] = None,
        duration: Optional[float] = None,
        error: Optional[Exception] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        API 호출을 문서화합니다.

        Args:
            operation: 작업 이름 (예: 'get_video_metadata', 'get_transcript')
            parameters: API 호출 파라미터
            result: API 호출 결과
            duration: 실행 시간 (초)
            error: 발생한 에러 (있는 경우)
            metadata: 추가 메타데이터
        """
        timestamp = datetime.now()
        call_id = f"{operation}_{timestamp.strftime('%Y%m%d_%H%M%S_%f')}"

        log_entry = {
            'call_id': call_id,
            'timestamp': timestamp.isoformat(),
            'operation': operation,
            'parameters': parameters,
            'success': error is None,
            'duration': duration,
            'metadata': metadata or {}
        }

        if result is not None:
            log_entry['result_summary'] = self._summarize_result(result)
            log_entry['result_size'] = len(json.dumps(result))

        if error is not None:
            log_entry['error'] = {
                'type': type(error).__name__,
                'message': str(error),
                'traceback': traceback.format_exc()
            }
            # Also document in error log
            self.document_error(
                operation=operation,
                error=error,
                context={'parameters': parameters}
            )

        # Add to in-memory log
        self.api_call_log.append(log_entry)

        # Write to file
        if self.enable_file_logging:
            log_file = self.api_calls_dir / f"{timestamp.strftime('%Y%m%d')}_api_calls.jsonl"
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')

        # Log message
        status = "SUCCESS" if error is None else "FAILED"
        duration_str = f" ({duration:.3f}s)" if duration else ""
        self.logger.info(f"API Call [{status}]: {operation}{duration_str}")

        if error:
            self.logger.error(f"Error in {operation}: {str(error)}")

    def document_error(
        self,
        operation: str,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        severity: str = 'error'
    ):
        """
        에러를 문서화합니다.

        Args:
            operation: 에러가 발생한 작업
            error: 에러 객체
            context: 에러 발생 컨텍스트
            severity: 심각도 (debug, info, warning, error, critical)
        """
        timestamp = datetime.now()
        error_id = f"{operation}_{timestamp.strftime('%Y%m%d_%H%M%S_%f')}"

        error_entry = {
            'error_id': error_id,
            'timestamp': timestamp.isoformat(),
            'operation': operation,
            'severity': severity,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'traceback': traceback.format_exc(),
            'context': context or {}
        }

        # Add to in-memory log
        self.error_log.append(error_entry)

        # Write to file
        if self.enable_file_logging:
            error_file = self.errors_dir / f"{timestamp.strftime('%Y%m%d')}_errors.jsonl"
            with open(error_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(error_entry, ensure_ascii=False) + '\n')

        # Log
        self.logger.error(f"Error documented: {operation} - {type(error).__name__}: {str(error)}")

    def document_performance(
        self,
        operation: str,
        duration: float,
        metrics: Optional[Dict[str, Any]] = None
    ):
        """
        성능 메트릭을 문서화합니다.

        Args:
            operation: 작업 이름
            duration: 실행 시간 (초)
            metrics: 추가 메트릭 (메모리 사용량, 처리 항목 수 등)
        """
        timestamp = datetime.now()

        perf_entry = {
            'timestamp': timestamp.isoformat(),
            'operation': operation,
            'duration': duration,
            'metrics': metrics or {}
        }

        # Add to in-memory log
        self.performance_log.append(perf_entry)

        # Write to file
        if self.enable_file_logging:
            perf_file = self.performance_dir / f"{timestamp.strftime('%Y%m%d')}_performance.jsonl"
            with open(perf_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(perf_entry, ensure_ascii=False) + '\n')

        self.logger.debug(f"Performance: {operation} - {duration:.3f}s")

    def generate_daily_report(
        self,
        date: Optional[datetime] = None,
        format: str = 'both'
    ) -> Dict[str, str]:
        """
        일일 로그 리포트를 생성합니다.

        Args:
            date: 리포트 날짜 (기본값: 오늘)
            format: 출력 형식 ('json', 'markdown', 'both')

        Returns:
            생성된 리포트 파일 경로 딕셔너리
        """
        if date is None:
            date = datetime.now()

        date_str = date.strftime('%Y%m%d')
        self.logger.info(f"Generating daily report for {date_str}")

        # Load all logs for the day
        api_calls = self._load_daily_logs(self.api_calls_dir, date_str)
        errors = self._load_daily_logs(self.errors_dir, date_str)
        performance = self._load_daily_logs(self.performance_dir, date_str)

        # Generate statistics
        stats = self._calculate_statistics(api_calls, errors, performance)

        report_files = {}

        # Generate JSON report
        if format in ['json', 'both']:
            json_file = self.reports_dir / f"daily_report_{date_str}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'date': date_str,
                    'statistics': stats,
                    'api_calls': api_calls,
                    'errors': errors,
                    'performance': performance
                }, f, ensure_ascii=False, indent=2)
            report_files['json'] = str(json_file)
            self.logger.info(f"JSON report saved: {json_file}")

        # Generate Markdown report
        if format in ['markdown', 'both']:
            md_file = self.reports_dir / f"daily_report_{date_str}.md"
            md_content = self._generate_markdown_report(date_str, stats, api_calls, errors, performance)
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(md_content)
            report_files['markdown'] = str(md_file)
            self.logger.info(f"Markdown report saved: {md_file}")

        return report_files

    def _load_daily_logs(self, directory: Path, date_str: str) -> List[Dict[str, Any]]:
        """특정 날짜의 로그를 로드합니다."""
        logs = []
        log_file = directory / f"{date_str}_*.jsonl"

        for file_path in directory.glob(f"{date_str}_*.jsonl"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            logs.append(json.loads(line))
            except Exception as e:
                self.logger.error(f"Failed to load log file {file_path}: {e}")

        return logs

    def _calculate_statistics(
        self,
        api_calls: List[Dict],
        errors: List[Dict],
        performance: List[Dict]
    ) -> Dict[str, Any]:
        """로그 데이터로부터 통계를 계산합니다."""
        stats = {
            'total_api_calls': len(api_calls),
            'successful_calls': sum(1 for call in api_calls if call.get('success', False)),
            'failed_calls': sum(1 for call in api_calls if not call.get('success', False)),
            'total_errors': len(errors),
            'error_types': defaultdict(int),
            'operations': defaultdict(int),
            'average_duration': 0,
            'total_duration': 0
        }

        # Count error types
        for error in errors:
            error_type = error.get('error_type', 'Unknown')
            stats['error_types'][error_type] += 1

        # Count operations
        for call in api_calls:
            operation = call.get('operation', 'Unknown')
            stats['operations'][operation] += 1

        # Calculate duration statistics
        durations = [call.get('duration', 0) for call in api_calls if call.get('duration')]
        if durations:
            stats['average_duration'] = sum(durations) / len(durations)
            stats['total_duration'] = sum(durations)
            stats['min_duration'] = min(durations)
            stats['max_duration'] = max(durations)

        # Convert defaultdict to dict for JSON serialization
        stats['error_types'] = dict(stats['error_types'])
        stats['operations'] = dict(stats['operations'])

        return stats

    def _generate_markdown_report(
        self,
        date_str: str,
        stats: Dict[str, Any],
        api_calls: List[Dict],
        errors: List[Dict],
        performance: List[Dict]
    ) -> str:
        """Markdown 형식의 리포트를 생성합니다."""
        md = f"# Daily Log Report - {date_str}\n\n"

        md += "## Summary\n\n"
        md += f"- **Total API Calls**: {stats['total_api_calls']}\n"
        md += f"- **Successful Calls**: {stats['successful_calls']}\n"
        md += f"- **Failed Calls**: {stats['failed_calls']}\n"
        md += f"- **Total Errors**: {stats['total_errors']}\n"

        if stats.get('average_duration'):
            md += f"- **Average Duration**: {stats['average_duration']:.3f}s\n"
            md += f"- **Total Duration**: {stats['total_duration']:.3f}s\n"

        md += "\n## Operations Breakdown\n\n"
        md += "| Operation | Count |\n"
        md += "|-----------|-------|\n"
        for operation, count in sorted(stats['operations'].items(), key=lambda x: x[1], reverse=True):
            md += f"| {operation} | {count} |\n"

        if stats['error_types']:
            md += "\n## Error Types\n\n"
            md += "| Error Type | Count |\n"
            md += "|------------|-------|\n"
            for error_type, count in sorted(stats['error_types'].items(), key=lambda x: x[1], reverse=True):
                md += f"| {error_type} | {count} |\n"

        # Recent errors (last 10)
        if errors:
            md += "\n## Recent Errors (Last 10)\n\n"
            for error in errors[-10:]:
                md += f"### {error.get('timestamp', 'Unknown Time')}\n"
                md += f"- **Operation**: {error.get('operation', 'Unknown')}\n"
                md += f"- **Type**: {error.get('error_type', 'Unknown')}\n"
                md += f"- **Message**: {error.get('error_message', 'No message')}\n\n"

        md += f"\n---\n*Generated at {datetime.now().isoformat()}*\n"

        return md

    def _summarize_result(self, result: Any) -> str:
        """API 결과를 요약합니다."""
        if isinstance(result, dict):
            keys = list(result.keys())
            return f"Dict with {len(keys)} keys: {', '.join(keys[:5])}"
        elif isinstance(result, list):
            return f"List with {len(result)} items"
        elif isinstance(result, str):
            return f"String (length: {len(result)})"
        else:
            return str(type(result).__name__)

    def clear_old_logs(self, days: int = 30):
        """
        오래된 로그 파일을 삭제합니다.

        Args:
            days: 보관 기간 (일)
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        cutoff_str = cutoff_date.strftime('%Y%m%d')

        deleted_count = 0

        for directory in [self.api_calls_dir, self.errors_dir, self.performance_dir]:
            for file_path in directory.glob('*.jsonl'):
                # Extract date from filename (e.g., "20231215_api_calls.jsonl")
                try:
                    file_date_str = file_path.stem.split('_')[0]
                    if file_date_str < cutoff_str:
                        file_path.unlink()
                        deleted_count += 1
                        self.logger.info(f"Deleted old log file: {file_path}")
                except Exception as e:
                    self.logger.error(f"Failed to delete {file_path}: {e}")

        self.logger.info(f"Deleted {deleted_count} old log files (older than {days} days)")

        return deleted_count


# Convenience functions for quick usage

_default_documenter: Optional[LogDocumenter] = None


def get_documenter() -> LogDocumenter:
    """기본 LogDocumenter 인스턴스를 가져옵니다."""
    global _default_documenter
    if _default_documenter is None:
        _default_documenter = LogDocumenter()
    return _default_documenter


def document_api_call(*args, **kwargs):
    """기본 documenter를 사용하여 API 호출을 문서화합니다."""
    get_documenter().document_api_call(*args, **kwargs)


def document_error(*args, **kwargs):
    """기본 documenter를 사용하여 에러를 문서화합니다."""
    get_documenter().document_error(*args, **kwargs)


def document_performance(*args, **kwargs):
    """기본 documenter를 사용하여 성능을 문서화합니다."""
    get_documenter().document_performance(*args, **kwargs)


def generate_daily_report(*args, **kwargs):
    """기본 documenter를 사용하여 일일 리포트를 생성합니다."""
    return get_documenter().generate_daily_report(*args, **kwargs)
