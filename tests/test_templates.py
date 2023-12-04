import re
import shutil
import subprocess
import tempfile
from collections.abc import Iterator
from pathlib import Path

import pytest

commit_pattern = re.compile(r"_commit: .*")
src_path_pattern = re.compile(r"_src_path: .*")
tests_path = Path(__file__).parent
root = tests_path.parent
generated_folder = "tests_generated"
generated_root = root / generated_folder

config_path = Path(__file__).parent.parent / "pyproject.toml"
NPM_INSTALL_ARGS = ["npm", "install"]
NPM_LINT_ARGS = ["npm", "run", "lint"]
NPM_BUILD_ARGS = ["npm", "run", "build"]


def _generate_default_parameters(
    default_state: str = "yes",
    cloud_provider: str = "none",
    ide_jetbrains: str = "no",
) -> dict[str, str]:
    return {
        "author_name": "None",
        "author_email": "None",
        "ide_vscode": default_state,
        "ide_jetbrains": ide_jetbrains,
        "use_eslint_prettier": default_state,
        "use_tailwind": default_state,
        "use_daisy_ui": default_state,
        "use_jest": default_state,
        "use_playwright": default_state,
        "use_github_actions": default_state,
        "cloud_provider": cloud_provider,
    }


@pytest.fixture(autouse=True, scope="module")
def working_dir() -> Iterator[Path]:
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp:
        working_dir = Path(temp) / "template"
        working_generated_root = working_dir / generated_folder
        shutil.copytree(root, working_dir)
        subprocess.run(["git", "add", "-A"], cwd=working_dir)
        subprocess.run(
            ["git", "commit", "-m", "draft changes", "--no-verify"], cwd=working_dir
        )

        yield working_dir

        for src_dir in working_generated_root.iterdir():
            if not src_dir.is_dir():
                continue

            dest_dir = generated_root / src_dir.stem
            shutil.rmtree(dest_dir, ignore_errors=True)
            shutil.copytree(src_dir, dest_dir, dirs_exist_ok=True)


def run_init(
    working_dir: Path,
    test_name: str,
    *args: str,
    template_url: str | None = None,
    template_branch: str | None = None,
    answers: dict[str, str] | None = None,
    custom_check_args: list[list[str]] | None = None,
) -> subprocess.CompletedProcess:
    copy_to = working_dir / generated_folder / test_name
    shutil.rmtree(copy_to, ignore_errors=True)
    if template_url is None:
        template_url = str(working_dir)

        if template_branch is None:
            git_output = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=working_dir,
                stdout=subprocess.PIPE,
            )
            template_branch = git_output.stdout.decode("utf-8").strip()

    init_args = [
        "algokit",
        "--verbose",
        "init",
        "--name",
        str(copy_to.stem),
        "--template-url",
        template_url,
        "--UNSAFE-SECURITY-accept-template-url",
        "--defaults",
        "--no-ide",
        "--no-git",
        "--no-bootstrap",
    ]
    answers = {
        **_generate_default_parameters("yes"),
        **(answers or {}),
    }

    for question, answer in answers.items():
        init_args.extend(["-a", question, str(answer)])
    if template_branch:
        init_args.extend(["--template-url-ref", template_branch])
    init_args.extend(args)

    result = subprocess.run(
        init_args,
        input="y",  # acknowledge that input is not a tty
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        cwd=copy_to.parent,
    )

    if result.returncode:
        return result
    # if successful, normalize .copier-answers.yml to make observing diffs easier
    copier_answers = Path(copy_to / ".copier-answers.yml")
    content = copier_answers.read_text("utf-8")
    content = commit_pattern.sub("_commit: <commit>", content)
    content = src_path_pattern.sub("_src_path: <src>", content)
    copier_answers.write_text(content, "utf-8")

    if custom_check_args:
        for check_args in custom_check_args:
            result = subprocess.run(
                check_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=copy_to,
            )
            if result.returncode:
                break

    # remove node_modules
    shutil.rmtree(copy_to / "node_modules", ignore_errors=True)

    # Check if .idea folder exists and if so modify os specific SDK_HOME path
    idea_folder = copy_to / ".idea"
    if idea_folder.exists():
        # Iterate over all files in .idea/runConfigurations
        for file in (idea_folder / "runConfigurations").iterdir():
            # Read the file content
            content = file.read_text()
            # Replace the line containing SDK_HOME
            content = re.sub(
                r'<option name="SDK_HOME" value=".*" />',
                '<option name="SDK_HOME" value="$PROJECT_DIR$/.venv/bin/python" />',
                content,
            )
            # Write the modified content back to the file
            file.write_text(content)
    return result


def test_all_default_parameters_on_vercel(working_dir: Path) -> None:
    response = run_init(
        working_dir,
        "test_all_default_parameters_on_vercel",
        answers=_generate_default_parameters("yes", "vercel"),
        custom_check_args=[NPM_INSTALL_ARGS, NPM_LINT_ARGS, NPM_BUILD_ARGS],
    )

    assert response.returncode == 0, response.stdout


def test_all_default_parameters_on_netlify(working_dir: Path) -> None:
    response = run_init(
        working_dir,
        "test_all_default_parameters_on_netlify",
        answers=_generate_default_parameters("yes", "netlify"),
        custom_check_args=[NPM_INSTALL_ARGS, NPM_LINT_ARGS, NPM_BUILD_ARGS],
    )

    assert response.returncode == 0, response.stdout


def test_all_default_parameters_off(working_dir: Path) -> None:
    response = run_init(
        working_dir,
        "test_all_default_parameters_off",
        answers=_generate_default_parameters("no"),
        custom_check_args=[NPM_INSTALL_ARGS, NPM_BUILD_ARGS],
    )

    assert response.returncode == 0, response.stdout


def test_all_default_parameters_off_jetbrains(working_dir: Path) -> None:
    response = run_init(
        working_dir,
        "test_all_default_parameters_jetbrains",
        answers=_generate_default_parameters("no", ide_jetbrains="yes"),
        custom_check_args=[NPM_INSTALL_ARGS, NPM_BUILD_ARGS],
    )

    assert response.returncode == 0, response.stdout
