"""Tests for exporter module."""

import pytest
import tempfile
import os
from datetime import datetime
from pathlib import Path

from news_ai.exporter import MarkdownExporter
from news_ai.models import (
    Feed,
    Entry,
    SummarizeResult,
    Highlight,
    SummaryReport,
)


class TestMarkdownExporter:
    """Test cases for MarkdownExporter."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def sample_result(self):
        """Create a sample SummarizeResult."""
        return SummarizeResult(
            summary="Test summary text",
            highlights=[
                Highlight(
                    title="Highlight 1",
                    source="Source 1",
                    summary="Description 1",
                    importance="high",
                ),
                Highlight(
                    title="Highlight 2",
                    source="Source 2",
                    summary="Description 2",
                    importance="medium",
                ),
            ],
            keywords=["keyword1", "keyword2"],
            sentiment="positive",
            generated_at=datetime(2024, 1, 1, 12, 0),
        )

    @pytest.fixture
    def sample_report(self, sample_result):
        """Create a sample SummaryReport."""
        feeds = [
            Feed(id=1, title="Feed 1", category="News"),
            Feed(id=2, title="Feed 2", category="Analysis"),
        ]
        entries = [
            Entry(
                id=1,
                title="Entry 1",
                url="http://example.com/1",
                published_at=datetime(2024, 1, 1, 10, 0),
                summary="Summary 1",
                feed_id=1,
                feed_title="Feed 1",
            ),
            Entry(
                id=2,
                title="Entry 2",
                url="http://example.com/2",
                published_at=datetime(2024, 1, 1, 11, 0),
                summary="Summary 2",
                feed_id=2,
                feed_title="Feed 2",
            ),
        ]
        return SummaryReport(
            result=sample_result,
            feeds=feeds,
            entries=entries,
            total_count=2,
        )

    def test_export_creates_file(self, temp_dir, sample_report):
        """Test export creates a markdown file."""
        exporter = MarkdownExporter(output_dir=temp_dir)

        filepath = exporter.export(sample_report)

        assert filepath is not None
        assert Path(filepath).exists()
        assert filepath.endswith(".md")

    def test_export_filename_format(self, temp_dir, sample_report):
        """Test exported file follows naming convention."""
        exporter = MarkdownExporter(output_dir=temp_dir)

        filepath = exporter.export(sample_report)

        filename = Path(filepath).name
        assert filename.startswith("news_summary_")
        assert filename.endswith(".md")

    def test_export_content_structure(self, temp_dir, sample_report):
        """Test exported file contains expected sections."""
        exporter = MarkdownExporter(output_dir=temp_dir)

        filepath = exporter.export(sample_report)

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        assert "# 新闻总结报告" in content
        assert "**生成时间**" in content or "生成时间" in content
        assert "Test summary text" in content
        assert "Highlight 1" in content
        assert "Highlight 2" in content
        assert "keyword1" in content
        assert "keyword2" in content

    def test_export_highlight_format(self, temp_dir, sample_report):
        """Test highlights are formatted correctly."""
        exporter = MarkdownExporter(output_dir=temp_dir)

        filepath = exporter.export(sample_report)

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        assert "### Highlight 1" in content or "## Highlight 1" in content
        assert "**来源**:" in content or "来源" in content
        assert "Description 1" in content

    def test_export_with_empty_feeds(self, temp_dir, sample_result):
        """Test export with empty feeds list."""
        report = SummaryReport(
            result=sample_result,
            feeds=[],
            entries=[],
            total_count=0,
        )
        exporter = MarkdownExporter(output_dir=temp_dir)

        filepath = exporter.export(report)

        assert Path(filepath).exists()

    def test_export_creates_directory(self, temp_dir, sample_report):
        """Test export creates output directory if needed."""
        new_dir = os.path.join(temp_dir, "subdir", "nested")
        exporter = MarkdownExporter(output_dir=new_dir)

        filepath = exporter.export(sample_report)

        assert Path(filepath).exists()
        assert new_dir in filepath

    def test_render_report(self, temp_dir, sample_report):
        """Test render_report returns string."""
        exporter = MarkdownExporter(output_dir=temp_dir)

        output = exporter.render_report(sample_report)

        assert isinstance(output, str)
        assert len(output) > 0
        assert "Test summary text" in output
