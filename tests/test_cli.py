import subprocess
import sys
from pathlib import Path

from dom_parser.cli import USAGE, main

REPO_ROOT = Path(__file__).resolve().parent.parent
SAMPLE = REPO_ROOT / "samples" / "sample.html"


def read_temp(tmp_path: Path, name: str, content: str) -> str:
    path = tmp_path / name
    path.write_text(content, encoding="utf-8")
    return str(path)


def test_prints_file_contents_unchanged(tmp_path, capsys):
    path = read_temp(tmp_path, "in.html", "<p>Hello</p>\n")
    assert main([path]) == 0
    assert capsys.readouterr().out == "<p>Hello</p>\n"


def test_does_not_add_trailing_newline(tmp_path, capsys):
    path = read_temp(tmp_path, "in.html", "<p>Hello</p>")
    assert main([path]) == 0
    assert capsys.readouterr().out == "<p>Hello</p>"


def test_preserves_interior_whitespace(tmp_path, capsys):
    content = "  <p>a</p>\n\n\n<p>b</p>\n"
    path = read_temp(tmp_path, "in.html", content)
    assert main([path]) == 0
    assert capsys.readouterr().out == content


def test_empty_file_is_valid(tmp_path, capsys):
    path = read_temp(tmp_path, "empty.html", "")
    assert main([path]) == 0
    captured = capsys.readouterr()
    assert captured.out == ""


def test_missing_file_reports_error(tmp_path, capsys):
    path = str(tmp_path / "does-not-exist.html")
    assert main([path]) == 1
    captured = capsys.readouterr()
    assert captured.err == f"Cannot open file: {path}\n"
    assert captured.out == ""


def test_directory_reports_error(tmp_path, capsys):
    assert main([str(tmp_path)]) == 1
    captured = capsys.readouterr()
    assert captured.err == f"Cannot open file: {tmp_path}\n"
    assert captured.out == ""


def test_no_arguments_prints_usage(capsys):
    assert main([]) == 1
    captured = capsys.readouterr()
    assert captured.err == f"{USAGE}\n"
    assert captured.out == ""


def test_too_many_arguments_prints_usage(tmp_path, capsys):
    path = read_temp(tmp_path, "in.html", "x")
    assert main([path, "extra"]) == 1
    captured = capsys.readouterr()
    assert captured.err == f"{USAGE}\n"
    assert captured.out == ""


def test_unknown_flag_prints_usage(capsys):
    assert main(["--bogus"]) == 1
    captured = capsys.readouterr()
    assert captured.err == f"{USAGE}\n"
    assert captured.out == ""


def test_module_invocation_prints_sample():
    result = subprocess.run(
        [sys.executable, "-m", "dom_parser", str(SAMPLE)],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        env={"PYTHONPATH": str(REPO_ROOT / "src")},
    )
    assert result.returncode == 0
    assert result.stdout == SAMPLE.read_text(encoding="utf-8")


def test_module_invocation_missing_file():
    missing = str(REPO_ROOT / "samples" / "nope.html")
    result = subprocess.run(
        [sys.executable, "-m", "dom_parser", missing],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        env={"PYTHONPATH": str(REPO_ROOT / "src")},
    )
    assert result.returncode != 0
    assert f"Cannot open file: {missing}" in result.stderr
