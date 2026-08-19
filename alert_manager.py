import json
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Any, Callable, Optional
from collections import defaultdict
from logger import get_logger

logger = get_logger(__name__)


class AlertLevel(Enum):
    """알림 심각도 레벨입니다."""
    INFO = 1
    WARNING = 2
    CRITICAL = 3


class AlertStatus(Enum):
    """알림 상태입니다."""
    ACTIVE = "active"
    RESOLVED = "resolved"
    ACKNOWLEDGED = "acknowledged"


class Alert:
    """개별 알림을 나타냅니다."""

    def __init__(
        self,
        name: str,
        level: AlertLevel,
        message: str,
        agent: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.name = name
        self.level = level
        self.message = message
        self.agent = agent
        self.metadata = metadata or {}
        self.created_at = datetime.now()
        self.status = AlertStatus.ACTIVE
        self.acknowledged_at = None

    def acknowledge(self) -> None:
        """알림을 인정합니다."""
        self.status = AlertStatus.ACKNOWLEDGED
        self.acknowledged_at = datetime.now()
        logger.info(f"알림 인정됨: {self.name}")

    def resolve(self) -> None:
        """알림을 해결합니다."""
        self.status = AlertStatus.RESOLVED
        logger.info(f"알림 해결됨: {self.name}")

    def to_dict(self) -> Dict[str, Any]:
        """알림을 딕셔너리로 변환합니다."""
        return {
            "name": self.name,
            "level": self.level.name,
            "message": self.message,
            "agent": self.agent,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "metadata": self.metadata
        }


class AlertRule:
    """알림 규칙입니다."""

    def __init__(
        self,
        name: str,
        condition: Callable[[Dict[str, Any]], bool],
        level: AlertLevel,
        message_template: str
    ):
        self.name = name
        self.condition = condition
        self.level = level
        self.message_template = message_template
        self.triggered_count = 0

    def evaluate(self, data: Dict[str, Any]) -> bool:
        """조건을 평가합니다."""
        try:
            result = self.condition(data)
            if result:
                self.triggered_count += 1
            return result
        except Exception as e:
            logger.error(f"규칙 평가 실패 ({self.name}): {e}")
            return False

    def format_message(self, data: Dict[str, Any]) -> str:
        """메시지 템플릿을 포매팅합니다."""
        try:
            return self.message_template.format(**data)
        except KeyError:
            return self.message_template


class AlertManager:
    """알림을 관리합니다."""

    def __init__(self, max_alerts: int = 1000):
        self.alerts: Dict[str, Alert] = {}
        self.rules: Dict[str, AlertRule] = {}
        self.max_alerts = max_alerts
        self.alert_history: List[Alert] = []
        self.handlers: List[Callable[[Alert], None]] = []

    def add_rule(self, rule: AlertRule) -> None:
        """알림 규칙을 추가합니다."""
        self.rules[rule.name] = rule
        logger.info(f"알림 규칙 추가됨: {rule.name}")

    def remove_rule(self, rule_name: str) -> None:
        """알림 규칙을 제거합니다."""
        if rule_name in self.rules:
            del self.rules[rule_name]
            logger.info(f"알림 규칙 제거됨: {rule_name}")

    def register_handler(self, handler: Callable[[Alert], None]) -> None:
        """알림 핸들러를 등록합니다."""
        self.handlers.append(handler)
        logger.debug("알림 핸들러 등록됨")

    def create_alert(
        self,
        name: str,
        level: AlertLevel,
        message: str,
        agent: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Alert:
        """알림을 생성합니다."""
        alert = Alert(name, level, message, agent, metadata)
        self.alerts[name] = alert
        self.alert_history.append(alert)

        if len(self.alerts) > self.max_alerts:
            oldest = min(self.alerts.values(), key=lambda a: a.created_at)
            del self.alerts[oldest.name]

        self._trigger_handlers(alert)
        logger.warning(f"알림 생성됨: {name} ({level.name})")
        return alert

    def _trigger_handlers(self, alert: Alert) -> None:
        """모든 핸들러를 트리거합니다."""
        for handler in self.handlers:
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"알림 핸들러 실행 실패: {e}")

    def evaluate_rules(self, data: Dict[str, Any]) -> List[Alert]:
        """모든 규칙을 평가하고 알림을 생성합니다."""
        created_alerts = []
        for rule_name, rule in self.rules.items():
            if rule.evaluate(data):
                message = rule.format_message(data)
                alert = self.create_alert(
                    f"{rule_name}_{datetime.now().timestamp()}",
                    rule.level,
                    message,
                    metadata=data
                )
                created_alerts.append(alert)
        return created_alerts

    def get_active_alerts(self) -> List[Alert]:
        """활성 알림을 반환합니다."""
        return [a for a in self.alerts.values() if a.status == AlertStatus.ACTIVE]

    def get_alerts_by_level(self, level: AlertLevel) -> List[Alert]:
        """특정 심각도의 알림을 반환합니다."""
        return [a for a in self.alerts.values() if a.level == level]

    def get_alerts_by_agent(self, agent: str) -> List[Alert]:
        """특정 에이전트의 알림을 반환합니다."""
        return [a for a in self.alerts.values() if a.agent == agent]

    def acknowledge_alert(self, alert_name: str) -> bool:
        """알림을 인정합니다."""
        if alert_name in self.alerts:
            self.alerts[alert_name].acknowledge()
            return True
        return False

    def resolve_alert(self, alert_name: str) -> bool:
        """알림을 해결합니다."""
        if alert_name in self.alerts:
            self.alerts[alert_name].resolve()
            return True
        return False

    def get_statistics(self) -> Dict[str, Any]:
        """알림 통계를 반환합니다."""
        stats = {
            "total_alerts": len(self.alert_history),
            "active_alerts": len(self.get_active_alerts()),
            "by_level": {},
            "by_agent": defaultdict(int),
            "rules_triggered": {}
        }

        for level in AlertLevel:
            stats["by_level"][level.name] = len(self.get_alerts_by_level(level))

        for alert in self.alerts.values():
            if alert.agent:
                stats["by_agent"][alert.agent] += 1

        for rule_name, rule in self.rules.items():
            stats["rules_triggered"][rule_name] = rule.triggered_count

        return stats

    def print_summary(self) -> None:
        """알림 요약을 출력합니다."""
        stats = self.get_statistics()
        print("\n" + "="*60)
        print("알림 관리자 요약")
        print("="*60)
        print(f"전체 알림: {stats['total_alerts']}")
        print(f"활성 알림: {stats['active_alerts']}")
        print("\n심각도별:")
        for level, count in stats["by_level"].items():
            print(f"  {level}: {count}")
        print("\n에이전트별:")
        for agent, count in stats["by_agent"].items():
            print(f"  {agent}: {count}")
        print("\n규칙 트리거:")
        for rule, count in stats["rules_triggered"].items():
            print(f"  {rule}: {count}")
        print("="*60 + "\n")


if __name__ == "__main__":
    manager = AlertManager()

    def log_alert(alert: Alert):
        print(f"[ALERT HANDLER] {alert.level.name}: {alert.message}")

    manager.register_handler(log_alert)
    print("AlertManager가 준비되었습니다.")
