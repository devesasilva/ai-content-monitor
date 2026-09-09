from prometheus_client import Counter, Histogram


content_analysis_total = Counter(
    "content_analysis_total",
    "Total de análises de conteúdo realizadas"
)

content_analysis_errors_total = Counter(
    "content_analysis_errors_total",
    "Total de erros durante análises de conteúdo"
)

content_analysis_duration_seconds = Histogram(
    "content_analysis_duration_seconds",
    "Tempo de duração das análises de conteúdo"
)

content_approved_total = Counter(
    "content_approved_total",
    "Total de conteúdos aprovados"
)

content_blocked_total = Counter(
    "content_blocked_total",
    "Total de conteúdos bloqueados"
)   