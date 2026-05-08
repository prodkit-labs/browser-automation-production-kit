from prodkit_browser.artifacts import ArtifactWriter


def test_artifact_writer_creates_nested_file(tmp_path) -> None:
    writer = ArtifactWriter(tmp_path)

    path = writer.write_text("nested/output.txt", "hello")

    assert (tmp_path / "nested" / "output.txt").read_text(encoding="utf-8") == "hello"
    assert path.endswith("nested/output.txt")
