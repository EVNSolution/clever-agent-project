from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]


class IssueResolutionContextWikiPromptTest(unittest.TestCase):
    def test_issue_resolution_context_wiki_prompt_is_available_and_linked(self):
        prompt_path = REPO_ROOT / "docs/templates/issue-resolution-context-wiki-prompt.md"
        setting_path = REPO_ROOT / "docs/setting.md"
        gitignore_path = REPO_ROOT / ".gitignore"

        self.assertTrue(prompt_path.exists())

        prompt = prompt_path.read_text(encoding="utf-8")
        self.assertIn("이슈 해결", prompt)
        self.assertIn(
            "`clever-context-monorepo/docs/services/<service>/index.md`", prompt
        )
        self.assertIn("`clever-context-monorepo/docs/wiki/`", prompt)
        self.assertIn("docs/wiki는 정본이 아니다", prompt)
        self.assertIn("해결 완료로 표시하기 전", prompt)

        setting = setting_path.read_text(encoding="utf-8")
        self.assertIn("issue-resolution-context-wiki-prompt.md", setting)

        gitignore = gitignore_path.read_text(encoding="utf-8")
        self.assertIn("!/docs/templates/issue-resolution-context-wiki-prompt.md", gitignore)

        context_doc = (
            REPO_ROOT.parent
            / "clever-context-monorepo/docs/root/doc-governance.md"
        ).read_text(encoding="utf-8")
        self.assertIn("PR 완료 시 context 판단", context_doc)
        self.assertIn("clever-context-monorepo update: <commit-or-PR>", context_doc)
        self.assertIn("`not-needed`", context_doc)
        self.assertIn("PR 정보와 운영 증거를 wiki에 올리지 않는다", context_doc)
        self.assertIn("외부 정본의 사실을 이 repo가 다시 설명하면 실패다", context_doc)
        self.assertIn("docs/services/<slice>/index.md", context_doc)

        self.assertNotIn("이슈 해결 시 context 정리 기준", context_doc)
        self.assertNotIn("dev/main PR review completion 기준", context_doc)
        self.assertNotIn(
            "검토 에이전트 작업은 wiki/service context 업데이트로 마친다",
            context_doc,
        )


if __name__ == "__main__":
    unittest.main()
