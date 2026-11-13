"""Issue #23: report HTML escaping + CDN integrity (offline)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from kis_backtest.report.generator import KISReportGenerator
from kis_backtest.report.themes import KISTheme


def test_title_is_escaped():
    gen = KISReportGenerator(theme=KISTheme())
    html = gen._build_html(
        title="<script>alert(1)</script>",
        subtitle="ok",
        components=[],
    )
    assert "<script>alert" not in html
    assert "&lt;script&gt;" in html


def test_subtitle_none_and_escaped():
    gen = KISReportGenerator(theme=KISTheme())
    html = gen._build_html(title="t", subtitle=None, components=[])
    assert "None" not in html
    html2 = gen._build_html(
        title="t", subtitle="<b>x</b>", components=[]
    )
    assert "&lt;b&gt;" in html2


def test_cdn_tags_have_integrity_and_crossorigin():
    gen = KISReportGenerator(theme=KISTheme())
    html = gen._build_html(title="t", subtitle="s", components=[])
    assert "https://cdn.plot.ly/plotly-3.3.1.min.js" in html
    assert "pretendard.css" in html
    assert html.count('integrity="sha384-') >= 2
    assert html.count('crossorigin="anonymous"') >= 2
