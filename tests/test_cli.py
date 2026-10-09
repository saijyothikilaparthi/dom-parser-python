import subprocess
import sys
from pathlib import Path

from dom_parser.cli import USAGE, main

REPO_ROOT = Path(__file__).resolve().parent.parent
SAMPLE = REPO_ROOT / "samples" / "sample.html"
FIXTURES = REPO_ROOT / "tests" / "fixtures"


def read_temp(tmp_path: Path, name: str, content: str) -> str:
    path = tmp_path / name
    path.write_text(content, encoding="utf-8")
    return str(path)


def write_bytes(tmp_path: Path, name: str, content: bytes) -> str:
    path = tmp_path / name
    path.write_bytes(content)
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


def test_preserves_lf_line_endings(tmp_path, capsys):
    content = b"<p>a</p>\n<p>b</p>\n"
    path = write_bytes(tmp_path, "lf.html", content)
    assert main([path]) == 0
    assert capsys.readouterr().out == content.decode("utf-8")


def test_preserves_crlf_line_endings(tmp_path, capsys):
    content = b"<p>a</p>\r\n<p>b</p>\r\n"
    path = write_bytes(tmp_path, "crlf.html", content)
    assert main([path]) == 0
    assert capsys.readouterr().out == content.decode("utf-8")


def test_preserves_missing_final_newline(tmp_path, capsys):
    content = b"<p>a</p>\r\n<p>b</p>"
    path = write_bytes(tmp_path, "no-final-newline.html", content)
    assert main([path]) == 0
    assert capsys.readouterr().out == content.decode("utf-8")


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
        check=False,
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
        check=False,
    )
    assert result.returncode != 0
    assert f"Cannot open file: {missing}" in result.stderr


def test_tokens_mode_prints_tokens_in_source_order(tmp_path, capsys):
    path = read_temp(tmp_path, "in.html", "<p>Hi</p>")
    assert main([path, "--tokens"]) == 0
    captured = capsys.readouterr()
    assert captured.out == "OPEN p\nTEXT 'Hi'\nCLOSE p\n"
    assert captured.err == ""


def test_tokens_mode_preserves_whitespace_only_text(tmp_path, capsys):
    path = read_temp(tmp_path, "in.html", "<p>a</p>\n  <p>b</p>")
    assert main([path, "--tokens"]) == 0
    assert capsys.readouterr().out == (
        "OPEN p\nTEXT 'a'\nCLOSE p\nTEXT '\\n  '\nOPEN p\nTEXT 'b'\nCLOSE p\n"
    )


def test_tokens_mode_requires_a_file(capsys):
    assert main(["--tokens"]) == 1
    captured = capsys.readouterr()
    assert captured.err == f"{USAGE}\n"
    assert captured.out == ""


def test_tokens_mode_missing_file_reports_error(tmp_path, capsys):
    path = str(tmp_path / "does-not-exist.html")
    assert main([path, "--tokens"]) == 1
    captured = capsys.readouterr()
    assert captured.err == f"Cannot open file: {path}\n"
    assert captured.out == ""


def test_tree_mode_prints_tree(tmp_path, capsys):
    path = read_temp(tmp_path, "in.html", "<html><body><p>Hello</p></body></html>")
    assert main([path, "--tree"]) == 0
    captured = capsys.readouterr()
    assert captured.out == (
        '.\n└── html\n    └── body\n        └── p\n            └── "Hello"\n'
    )
    assert captured.err == ""


def test_tree_mode_requires_a_file(capsys):
    assert main(["--tree"]) == 1
    captured = capsys.readouterr()
    assert captured.err == f"{USAGE}\n"
    assert captured.out == ""


def test_tree_mode_missing_file_reports_error(tmp_path, capsys):
    path = str(tmp_path / "does-not-exist.html")
    assert main([path, "--tree"]) == 1
    captured = capsys.readouterr()
    assert captured.err == f"Cannot open file: {path}\n"
    assert captured.out == ""


def test_tree_mode_renders_attributes(tmp_path, capsys):
    path = read_temp(tmp_path, "in.html", '<div id="main" class="box">x</div>')
    assert main([path, "--tree"]) == 0
    captured = capsys.readouterr()
    assert captured.out == '.\n└── div [id="main", class="box"]\n    └── "x"\n'
    assert captured.err == ""


def test_unclosed_fixture_reports_error(capsys):
    assert main([str(FIXTURES / "unclosed.html"), "--tree"]) == 1
    captured = capsys.readouterr()
    assert captured.err == "Unclosed tag: <div>\n"
    assert captured.out == ""


def test_unexpected_close_fixture_reports_error(capsys):
    assert main([str(FIXTURES / "unexpected_close.html"), "--tree"]) == 1
    captured = capsys.readouterr()
    assert captured.err == "Unexpected closing tag: </section>\n"
    assert captured.out == ""


def test_wrong_nesting_fixture_reports_error(capsys):
    assert main([str(FIXTURES / "wrong_nesting.html"), "--tree"]) == 1
    captured = capsys.readouterr()
    assert captured.err == "Unexpected closing tag: </b> (expected </i>)\n"
    assert captured.out == ""


def test_tree_mode_stops_at_first_error(tmp_path, capsys):
    path = read_temp(tmp_path, "in.html", "</section><div></div>")
    assert main([path, "--tree"]) == 1
    captured = capsys.readouterr()
    assert captured.err == "Unexpected closing tag: </section>\n"
    assert captured.out == ""


def test_text_mode_prints_text_nodes_one_per_line(tmp_path, capsys):
    path = read_temp(tmp_path, "in.html", "<div>\n  <p>One</p>\n  <p>Two</p>\n</div>\n")
    assert main([path, "--text"]) == 0
    captured = capsys.readouterr()
    assert captured.out == "One\nTwo\n"
    assert captured.err == ""


def test_text_mode_no_text_prints_nothing(tmp_path, capsys):
    path = read_temp(tmp_path, "in.html", "<div></div>")
    assert main([path, "--text"]) == 0
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_find_tag_mode_prints_matching_subtrees(tmp_path, capsys):
    path = read_temp(tmp_path, "in.html", "<div><p>x</p><p>y</p></div>")
    assert main([path, "--find-tag", "p"]) == 0
    captured = capsys.readouterr()
    assert captured.out == ('.\n├── p\n│   └── "x"\n└── p\n    └── "y"\n')
    assert captured.err == ""


def test_find_id_mode_matches_exactly_and_renders_each(tmp_path, capsys):
    path = read_temp(tmp_path, "in.html", '<div id="main"><p id="main">x</p></div>')
    assert main([path, "--find-id", "main"]) == 0
    captured = capsys.readouterr()
    assert captured.out == (
        ".\n"
        '├── div [id="main"]\n'
        '│   └── p [id="main"]\n'
        '│       └── "x"\n'
        '└── p [id="main"]\n'
        '    └── "x"\n'
    )
    assert captured.err == ""


def test_find_class_mode_matches_one_token_of_several(tmp_path, capsys):
    path = read_temp(tmp_path, "in.html", '<p class="a b">x</p><p class="c">y</p>')
    assert main([path, "--find-class", "a"]) == 0
    captured = capsys.readouterr()
    assert captured.out == '.\n└── p [class="a b"]\n    └── "x"\n'
    assert captured.err == ""


def test_find_class_mode_includes_nested_matches(tmp_path, capsys):
    path = read_temp(tmp_path, "in.html", '<div class="a"><div class="a">x</div></div>')
    assert main([path, "--find-class", "a"]) == 0
    captured = capsys.readouterr()
    assert captured.out == (
        ".\n"
        '├── div [class="a"]\n'
        '│   └── div [class="a"]\n'
        '│       └── "x"\n'
        '└── div [class="a"]\n'
        '    └── "x"\n'
    )
    assert captured.err == ""


def test_find_no_match_prints_nothing_and_succeeds(tmp_path, capsys):
    path = read_temp(tmp_path, "in.html", "<p>x</p>")
    assert main([path, "--find-tag", "zzz"]) == 0
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_find_tag_missing_value_prints_usage(tmp_path, capsys):
    path = read_temp(tmp_path, "in.html", "<p>x</p>")
    assert main([path, "--find-tag"]) == 1
    captured = capsys.readouterr()
    assert captured.err == f"{USAGE}\n"
    assert captured.out == ""


def test_find_tag_invalid_html_reports_error(tmp_path, capsys):
    path = read_temp(tmp_path, "in.html", "</span>")
    assert main([path, "--find-tag", "div"]) == 1
    captured = capsys.readouterr()
    assert captured.err == "Unexpected closing tag: </span>\n"
    assert captured.out == ""
