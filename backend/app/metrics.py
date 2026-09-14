from opentelemetry import metrics

meter = metrics.get_meter("ai_content_monitor")

content_analysis_total = meter.create_counter(
    name="content_analysis_total",
    description="Total de analises de conteudo realizadas"
)

content_analysis_errors_total = meter.create_counter(
    name="content_analysis_errors_total",
    description="Total de erros durante analises de conteudo"
)

content_approved_total = meter.create_counter(
    name="content_approved_total",
    description="Total de conteudos aprovados"
)

content_blocked_total = meter.create_counter(
    name="content_blocked_total",
    description="Total de conteudos bloqueados"
)

content_analysis_duration_seconds = meter.create_histogram(
    name="content_analysis_duration_seconds",
    description="Tempo de duracao das analises de conteudo",
    unit="s"
)
