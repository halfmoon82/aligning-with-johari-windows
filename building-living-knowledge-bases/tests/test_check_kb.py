import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_ROOT / "scripts" / "check_kb.py"
BLADES = ("Paradox", "Leverage", "Root cause", "Inversion", "Analogy", "Plain language", "Scale")


class CheckKnowledgeBaseTests(unittest.TestCase):
    def run_check(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(root), "--json"],
            text=True,
            capture_output=True,
            check=False,
        )

    def make_healthy_kb(self, root: Path) -> None:
        (root / "raw" / "finance").mkdir(parents=True)
        (root / "wiki" / "finance").mkdir(parents=True)
        (root / "KB_SCHEMA.md").write_text("# Knowledge Base Schema\n")
        (root / "raw" / "finance" / "report.md").write_text(
            "---\n"
            "source_type: note\n"
            "source: Source report\n"
            "collected: 2026-07-30\n"
            "published: 2026-07-01\n"
            "---\n\n"
            "# Source report\n\nRevenue increased 42% on 2026-07-01.\n"
        )
        (root / "wiki" / "finance" / "revenue.md").write_text(
            "# Revenue trend\n\n"
            "Type: Knowledge\n"
            "Updated: 2026-07-30\n"
            "Status: Active\n"
            "Seven-Blades: Complete\n"
            "Four-Gates: Pass\n"
            "Sources: [Source report](../../raw/finance/report.md)\n"
            "Raw: [Source report](../../raw/finance/report.md)\n\n"
            "## Synthesis\n\nRevenue increased 42% on 2026-07-01.\n"
            "\n## Seven-blade analysis\n\n"
            "- **Paradox:** Growth can coexist with weaker margins.\n"
            "- **Leverage:** Retention is the key multiplier.\n"
            "- **Root cause:** The report attributes the change to demand.\n"
            "- **Inversion:** No material finding — reversing the claim changes its scope.\n"
            "- **Analogy:** The pattern resembles compounding retention.\n"
            "- **Plain language:** Revenue grew in the reported period.\n"
            "- **Scale:** The conclusion is limited to the reported scope.\n"
            "\n## Evidence and reasoning\n\n"
            "- **Verified fact:** Revenue increased 42% on 2026-07-01.\n"
        )
        (root / "wiki" / "index.md").write_text(
            "# Knowledge Base Index\n\n## Finance\n\n- [Revenue trend](finance/revenue.md) — Current revenue evidence.\n"
        )
        (root / "wiki" / "log.md").write_text(
            "# Knowledge Base Log\n\n"
            "## [2026-07-30] ingest | Source report\n"
            "- Disposition: New\n"
            "- Raw: raw/finance/report.md\n"
            "- Updated: wiki/finance/revenue.md\n"
            "- Seven-Blades: Complete\n"
            "- Four-Gates: Pass\n"
        )

    def test_healthy_kb_passes_and_emits_counts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_healthy_kb(root)
            result = self.run_check(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "healthy")
            self.assertEqual(payload["counts"]["raw_files"], 1)
            self.assertEqual(payload["counts"]["wiki_articles"], 1)
            self.assertEqual(payload["counts"]["dispositions"], {"New": 1})
            self.assertEqual(payload["counts"]["seven_blade_complete"], 1)
            self.assertEqual(payload["counts"]["four_gate_results"], {"Pass": 1})

    def test_reports_broken_links_and_missing_index_entries(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_healthy_kb(root)
            extra = root / "wiki" / "finance" / "extra.md"
            extra.write_text(
                "# Extra\n\nType: Synthesis\nUpdated: 2026-07-30\nStatus: Active\n\n"
                "See [Missing](missing.md).\n"
            )
            result = self.run_check(root)
            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            codes = {item["code"] for item in payload["findings"]}
            self.assertIn("broken-link", codes)
            self.assertIn("missing-index-entry", codes)

    def test_reports_high_signal_claim_not_present_in_linked_raw(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_healthy_kb(root)
            article = root / "wiki" / "finance" / "revenue.md"
            article.write_text(article.read_text().replace("42%", "73%"))
            result = self.run_check(root)
            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            suspects = [item for item in payload["findings"] if item["code"] == "evidence-literal-missing"]
            self.assertTrue(any("73%" in item["message"] for item in suspects))

    def test_no_material_log_accounts_for_unreferenced_raw(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_healthy_kb(root)
            extra = root / "raw" / "finance" / "duplicate.md"
            extra.write_text(
                "---\nsource_type: note\nsource: Duplicate source\ncollected: 2026-07-30\npublished: Unknown\n---\n\n"
                "# Duplicate source\n"
            )
            log = root / "wiki" / "log.md"
            log.write_text(
                log.read_text()
                + "\n## [2026-07-30] ingest | no material: raw/finance/duplicate.md\n"
                + "- Disposition: No material\n"
                + "- Raw: raw/finance/duplicate.md\n"
            )
            result = self.run_check(root)
            payload = json.loads(result.stdout)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertNotIn("untracked-raw", {item["code"] for item in payload["findings"]})

    def test_logged_unicode_raw_path_with_spaces_is_accounted_for(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_healthy_kb(root)
            extra = root / "raw" / "中文 资料" / "重复 笔记.md"
            extra.parent.mkdir()
            extra.write_text(
                "---\nsource_type: note\nsource: 重复资料\ncollected: 2026-07-30\npublished: Unknown\n---\n\n"
                "# 重复资料\n"
            )
            log = root / "wiki" / "log.md"
            log.write_text(
                log.read_text()
                + "\n## [2026-07-30] ingest | no material: 重复笔记\n"
                + "- Disposition: No material\n"
                + "- Raw: <raw/中文 资料/重复 笔记.md>\n"
            )
            result = self.run_check(root)
            payload = json.loads(result.stdout)
            untracked_paths = {
                item["path"] for item in payload["findings"] if item["code"] == "untracked-raw"
            }
            self.assertNotIn("raw/中文 资料/重复 笔记.md", untracked_paths)

    def test_valid_synthesis_with_local_wiki_source_and_not_pass_is_healthy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_healthy_kb(root)
            synthesis = root / "wiki" / "finance" / "summary.md"
            synthesis.write_text(
                "# Finance summary\n\n"
                "Type: Synthesis\n"
                "Updated: 2026-07-30\n"
                "Status: Active\n"
                "Seven-Blades: Complete\n"
                "Four-Gates: Not pass\n"
                "Sources: [Revenue trend](revenue.md)\n\n"
                "## Synthesis\n\nThe source article supports a scoped revenue trend.\n\n"
                "## Seven-blade analysis\n\n"
                "- **Paradox:** Growth can coexist with weaker margins.\n"
                "- **Leverage:** Retention is the key multiplier.\n"
                "- **Root cause:** The source article identifies demand.\n"
                "- **Inversion:** No material finding — the reverse needs separate evidence.\n"
                "- **Analogy:** The pattern resembles compounding retention.\n"
                "- **Plain language:** The trend is limited to its source.\n"
                "- **Scale:** The scope should not be generalized.\n"
            )
            index = root / "wiki" / "index.md"
            index.write_text(index.read_text() + "- [Finance summary](finance/summary.md) — Saved synthesis.\n")

            result = self.run_check(root)
            payload = json.loads(result.stdout)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(payload["counts"]["four_gate_results"], {"Not pass": 1, "Pass": 1})

    def test_missing_structure_is_configuration_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_check(Path(tmp))
            self.assertEqual(result.returncode, 2)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "error")

    def test_requires_every_seven_blade_item(self) -> None:
        for blade in BLADES:
            with self.subTest(blade=blade), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                self.make_healthy_kb(root)
                article = root / "wiki" / "finance" / "revenue.md"
                lines = [line for line in article.read_text().splitlines() if not line.startswith(f"- **{blade}:**")]
                article.write_text("\n".join(lines) + "\n")

                result = self.run_check(root)

                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                codes = {item["code"] for item in json.loads(result.stdout)["findings"]}
                self.assertIn("missing-seven-blade", codes)

    def test_rejects_empty_blade_but_accepts_explained_no_material_finding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_healthy_kb(root)
            article = root / "wiki" / "finance" / "revenue.md"
            article.write_text(article.read_text().replace(
                "- **Scale:** The conclusion is limited to the reported scope.",
                "- **Scale:**",
            ))

            result = self.run_check(root)

            self.assertEqual(result.returncode, 1)
            self.assertIn("empty-seven-blade", {item["code"] for item in json.loads(result.stdout)["findings"]})

    def test_no_material_finding_marker_requires_actual_reason(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_healthy_kb(root)
            article = root / "wiki" / "finance" / "revenue.md"
            article.write_text(article.read_text().replace(
                "No material finding — reversing the claim changes its scope.",
                "No material finding —",
            ))

            result = self.run_check(root)

            self.assertEqual(result.returncode, 1)
            self.assertIn("empty-seven-blade", {item["code"] for item in json.loads(result.stdout)["findings"]})

    def test_pass_and_not_pass_are_both_valid_soft_gate_results(self) -> None:
        for gate_result in ("Pass", "Not pass"):
            with self.subTest(gate_result=gate_result), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                self.make_healthy_kb(root)
                article = root / "wiki" / "finance" / "revenue.md"
                article.write_text(article.read_text().replace("Four-Gates: Pass", f"Four-Gates: {gate_result}"))

                result = self.run_check(root)
                payload = json.loads(result.stdout)

                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual(payload["counts"]["article_statuses"], {"Active": 1})
                self.assertEqual(payload["counts"]["four_gate_results"], {gate_result: 1})

    def test_rejects_missing_or_invalid_four_gate_flag(self) -> None:
        for replacement in ("", "Four-Gates: Maybe"):
            with self.subTest(replacement=replacement), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                self.make_healthy_kb(root)
                article = root / "wiki" / "finance" / "revenue.md"
                article.write_text(article.read_text().replace("Four-Gates: Pass", replacement))

                result = self.run_check(root)

                self.assertEqual(result.returncode, 1)
                codes = {item["code"] for item in json.loads(result.stdout)["findings"]}
                self.assertTrue({"missing-four-gates", "invalid-four-gates"} & codes)

    def test_reports_missing_article_metadata_fields(self) -> None:
        for field in ("Type", "Updated", "Status", "Sources"):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                self.make_healthy_kb(root)
                article = root / "wiki" / "finance" / "revenue.md"
                lines = [line for line in article.read_text().splitlines() if not line.startswith(f"{field}:")]
                article.write_text("\n".join(lines) + "\n")

                result = self.run_check(root)

                self.assertEqual(result.returncode, 1)
                self.assertIn("missing-article-field", {item["code"] for item in json.loads(result.stdout)["findings"]})

    def test_reports_invalid_raw_frontmatter(self) -> None:
        cases = {
            "missing-source": "source: Source report\n",
            "invalid-source-type": "source_type: note\n",
            "invalid-url-source": "source_type: note\n",
            "invalid-collected": "collected: 2026-07-30\n",
            "invalid-published": "published: 2026-07-01\n",
        }
        replacements = {
            "missing-source": "",
            "invalid-source-type": "source_type: website\n",
            "invalid-url-source": "source_type: url\n",
            "invalid-collected": "collected: yesterday\n",
            "invalid-published": "published: someday\n",
        }
        for name, original in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                self.make_healthy_kb(root)
                raw = root / "raw" / "finance" / "report.md"
                raw.write_text(raw.read_text().replace(original, replacements[name]))

                result = self.run_check(root)

                self.assertEqual(result.returncode, 1)
                self.assertIn("invalid-raw-metadata", {item["code"] for item in json.loads(result.stdout)["findings"]})

    def test_raw_source_requires_nonempty_body(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_healthy_kb(root)
            raw = root / "raw" / "finance" / "report.md"
            raw.write_text(
                "---\nsource_type: note\nsource: Source report\ncollected: 2026-07-30\npublished: Unknown\n---\n"
            )

            result = self.run_check(root)

            self.assertEqual(result.returncode, 1)
            self.assertIn("invalid-raw-metadata", {item["code"] for item in json.loads(result.stdout)["findings"]})

    def test_url_only_raw_link_does_not_satisfy_knowledge_article(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_healthy_kb(root)
            article = root / "wiki" / "finance" / "revenue.md"
            article.write_text(article.read_text().replace(
                "Raw: [Source report](../../raw/finance/report.md)",
                "Raw: [Source report](https://example.com/report)",
            ))

            result = self.run_check(root)

            self.assertEqual(result.returncode, 1)
            self.assertIn("missing-local-raw", {item["code"] for item in json.loads(result.stdout)["findings"]})

    def test_gitkeep_cannot_satisfy_raw_evidence_requirement(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_healthy_kb(root)
            (root / "raw" / ".gitkeep").write_text("")
            article = root / "wiki" / "finance" / "revenue.md"
            article.write_text(article.read_text().replace(
                "Raw: [Source report](../../raw/finance/report.md)",
                "Raw: [Sentinel](../../raw/.gitkeep)",
            ))

            result = self.run_check(root)

            self.assertEqual(result.returncode, 1)
            self.assertIn("missing-local-raw", {item["code"] for item in json.loads(result.stdout)["findings"]})

    def test_synthesis_requires_existing_local_wiki_sources(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_healthy_kb(root)
            article = root / "wiki" / "finance" / "revenue.md"
            text = article.read_text().replace("Type: Knowledge", "Type: Synthesis")
            text = text.replace("Sources: [Source report](../../raw/finance/report.md)\n", "")
            text = text.replace("Raw: [Source report](../../raw/finance/report.md)\n", "")
            article.write_text(text)

            result = self.run_check(root)

            self.assertEqual(result.returncode, 1)
            self.assertIn("missing-synthesis-sources", {item["code"] for item in json.loads(result.stdout)["findings"]})

    def test_synthesis_index_link_is_not_an_article_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_healthy_kb(root)
            article = root / "wiki" / "finance" / "revenue.md"
            text = article.read_text().replace("Type: Knowledge", "Type: Synthesis")
            text = text.replace("Sources: [Source report](../../raw/finance/report.md)", "Sources: [Index](../index.md)")
            text = text.replace("Raw: [Source report](../../raw/finance/report.md)\n", "")
            article.write_text(text)

            result = self.run_check(root)

            self.assertEqual(result.returncode, 1)
            self.assertIn("missing-synthesis-sources", {item["code"] for item in json.loads(result.stdout)["findings"]})

    def test_synthesis_directory_source_returns_structured_finding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_healthy_kb(root)
            article = root / "wiki" / "finance" / "revenue.md"
            text = article.read_text().replace("Type: Knowledge", "Type: Synthesis")
            text = text.replace("Sources: [Source report](../../raw/finance/report.md)", "Sources: [Wiki directory](..)")
            text = text.replace("Raw: [Source report](../../raw/finance/report.md)\n", "")
            article.write_text(text)

            result = self.run_check(root)
            payload = json.loads(result.stdout)

            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertEqual(payload["status"], "findings")
            self.assertIn("missing-synthesis-sources", {item["code"] for item in payload["findings"]})

    def test_synthesis_lineage_must_reach_knowledge_with_valid_raw(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_healthy_kb(root)

            def synthesis_text(title: str, source: str) -> str:
                return (
                    f"# {title}\n\n"
                    "Type: Synthesis\nUpdated: 2026-07-30\nStatus: Active\n"
                    "Seven-Blades: Complete\nFour-Gates: Pass\n"
                    f"Sources: [Other synthesis]({source})\n\n"
                    "## Synthesis\n\nA derived conclusion.\n\n"
                    "## Seven-blade analysis\n\n"
                    "- **Paradox:** The conclusion has a bounded tension.\n"
                    "- **Leverage:** One variable controls the result.\n"
                    "- **Root cause:** The cited page describes the mechanism.\n"
                    "- **Inversion:** No material finding — the reverse needs evidence.\n"
                    "- **Analogy:** The structure resembles another bounded claim.\n"
                    "- **Plain language:** The conclusion is derived.\n"
                    "- **Scale:** The conclusion is scope-limited.\n"
                )

            (root / "wiki" / "finance" / "a.md").write_text(synthesis_text("A", "b.md"))
            (root / "wiki" / "finance" / "b.md").write_text(synthesis_text("B", "a.md"))
            index = root / "wiki" / "index.md"
            index.write_text(
                index.read_text()
                + "- [A](finance/a.md) — Cyclic synthesis.\n"
                + "- [B](finance/b.md) — Cyclic synthesis.\n"
            )

            result = self.run_check(root)

            self.assertEqual(result.returncode, 1)
            self.assertIn("invalid-synthesis-lineage", {item["code"] for item in json.loads(result.stdout)["findings"]})

    def test_checks_claim_before_first_section_heading(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_healthy_kb(root)
            article = root / "wiki" / "finance" / "revenue.md"
            article.write_text(article.read_text().replace(
                "Raw: [Source report](../../raw/finance/report.md)\n\n",
                "Raw: [Source report](../../raw/finance/report.md)\n\nProfit increased 73%.\n\n",
            ))

            result = self.run_check(root)

            suspects = [item for item in json.loads(result.stdout)["findings"] if item["code"] == "evidence-literal-missing"]
            self.assertTrue(any("73%" in item["message"] for item in suspects))

    def test_checks_number_with_plain_language_unit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_healthy_kb(root)
            article = root / "wiki" / "finance" / "revenue.md"
            article.write_text(article.read_text().replace(
                "Revenue increased 42% on 2026-07-01.",
                "Revenue increased 42% on 2026-07-01 and persisted for 3 months.",
                1,
            ))

            result = self.run_check(root)
            suspects = [item for item in json.loads(result.stdout)["findings"] if item["code"] == "evidence-literal-missing"]

            self.assertTrue(any("3 months" in item["message"] for item in suspects))

    def test_checks_short_direct_quote(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_healthy_kb(root)
            article = root / "wiki" / "finance" / "revenue.md"
            article.write_text(article.read_text().replace(
                "Revenue increased 42% on 2026-07-01.",
                'Revenue increased 42% on 2026-07-01 and was described as "Boom".',
                1,
            ))

            result = self.run_check(root)
            suspects = [item for item in json.loads(result.stdout)["findings"] if item["code"] == "evidence-literal-missing"]

            self.assertTrue(any("Boom" in item["message"] for item in suspects))

    def test_conflict_metadata_date_is_not_an_evidence_literal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_healthy_kb(root)
            raw2 = root / "raw" / "finance" / "counterpoint.md"
            raw2.write_text(
                "---\nsource_type: note\nsource: Counterpoint\ncollected: 2026-07-30\npublished: Unknown\n---\n\n"
                "# Counterpoint\n\nRevenue did not increase in the narrower segment.\n"
            )
            article = root / "wiki" / "finance" / "revenue.md"
            text = article.read_text().replace("Status: Active", "Status: Disputed")
            text = text.replace(
                "Raw: [Source report](../../raw/finance/report.md)",
                "Raw: [Source report](../../raw/finance/report.md), [Counterpoint](../../raw/finance/counterpoint.md)",
            )
            text += (
                "\n## Conflicts\n\n"
                "> **Status: Disputed**\n"
                "> Since: 2026-07-29\n"
                "> Why: The sources use different segment scopes.\n"
                "> Sources: [Source report](../../raw/finance/report.md), [Counterpoint](../../raw/finance/counterpoint.md)\n"
            )
            article.write_text(text)

            result = self.run_check(root)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(json.loads(result.stdout)["counts"]["evidence_suspects"], 0)

    def test_disputed_article_requires_complete_conflict_block(self) -> None:
        cases = {
            "missing-since": "> Since: 2026-07-29\n",
            "missing-why": "> Why: Different scopes.\n",
            "one-source": "> Sources: [Source report](../../raw/finance/report.md), [Counterpoint](../../raw/finance/counterpoint.md)\n",
        }
        for name, removed_line in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                self.make_healthy_kb(root)
                raw2 = root / "raw" / "finance" / "counterpoint.md"
                raw2.write_text(
                    "---\nsource_type: note\nsource: Counterpoint\ncollected: 2026-07-30\npublished: Unknown\n---\n"
                )
                article = root / "wiki" / "finance" / "revenue.md"
                text = article.read_text().replace("Status: Active", "Status: Disputed")
                text = text.replace(
                    "Raw: [Source report](../../raw/finance/report.md)",
                    "Raw: [Source report](../../raw/finance/report.md), [Counterpoint](../../raw/finance/counterpoint.md)",
                )
                block = (
                    "\n## Conflicts\n\n"
                    "> **Status: Disputed**\n"
                    "> Since: 2026-07-29\n"
                    "> Why: Different scopes.\n"
                    "> Sources: [Source report](../../raw/finance/report.md), [Counterpoint](../../raw/finance/counterpoint.md)\n"
                )
                if name == "one-source":
                    block = block.replace(removed_line, "> Sources: [Source report](../../raw/finance/report.md)\n")
                else:
                    block = block.replace(removed_line, "")
                article.write_text(text + block)

                result = self.run_check(root)

                self.assertEqual(result.returncode, 1)
                self.assertIn("invalid-conflict-block", {item["code"] for item in json.loads(result.stdout)["findings"]})

    def test_conflict_sources_must_be_files_not_directories(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_healthy_kb(root)
            article = root / "wiki" / "finance" / "revenue.md"
            text = article.read_text().replace("Status: Active", "Status: Disputed")
            text += (
                "\n## Conflicts\n\n"
                "> **Status: Disputed**\n"
                "> Since: 2026-07-29\n"
                "> Why: The positions use different scopes.\n"
                "> Sources: [Raw directory](../../raw), [Wiki directory](..)\n"
            )
            article.write_text(text)

            result = self.run_check(root)

            self.assertEqual(result.returncode, 1)
            self.assertIn("invalid-conflict-block", {item["code"] for item in json.loads(result.stdout)["findings"]})

    def test_conflict_sources_cannot_be_infrastructure_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_healthy_kb(root)
            article = root / "wiki" / "finance" / "revenue.md"
            text = article.read_text().replace("Status: Active", "Status: Disputed")
            text += (
                "\n## Conflicts\n\n"
                "> **Status: Disputed**\n"
                "> Since: 2026-07-29\n"
                "> Why: These are not source positions.\n"
                "> Sources: [Schema](../../KB_SCHEMA.md), [Index](../index.md)\n"
            )
            article.write_text(text)

            result = self.run_check(root)

            self.assertEqual(result.returncode, 1)
            self.assertIn("invalid-conflict-block", {item["code"] for item in json.loads(result.stdout)["findings"]})

    def test_duplicate_article_metadata_fields_are_rejected(self) -> None:
        cases = {
            "Status": "Status: Active\nStatus: Disputed\n",
            "Four-Gates": "Four-Gates: Pass\nFour-Gates: Not pass\n",
            "Raw": (
                "Raw: [Source report](../../raw/finance/report.md)\n"
                "Raw: [Source report](../../raw/finance/report.md)\n"
            ),
        }
        for field, doubled in cases.items():
            with self.subTest(field=field), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                self.make_healthy_kb(root)
                article = root / "wiki" / "finance" / "revenue.md"
                original = next(line for line in article.read_text().splitlines() if line.startswith(f"{field}:")) + "\n"
                article.write_text(article.read_text().replace(original, doubled))

                result = self.run_check(root)

                self.assertEqual(result.returncode, 1)
                self.assertIn("duplicate-article-field", {item["code"] for item in json.loads(result.stdout)["findings"]})

    def test_latest_valid_disposition_wins_for_each_raw_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_healthy_kb(root)
            log = root / "wiki" / "log.md"
            log.write_text(
                "# Knowledge Base Log\n\n"
                "## [2026-07-29] activate | Source report\n"
                "- Disposition: Needs update\n"
                "- Raw: raw/finance/report.md\n\n"
                "## [2026-07-30] activate | Source report\n"
                "- Disposition: Active\n"
                "- Raw: raw/finance/report.md\n"
                "- Updated: wiki/finance/revenue.md\n"
                "- Seven-Blades: Complete\n"
                "- Four-Gates: Not pass\n"
            )

            result = self.run_check(root)
            payload = json.loads(result.stdout)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(payload["counts"]["source_dispositions"], {"Active": 1})
            self.assertEqual(payload["counts"]["dispositions"], {"Active": 1})
            self.assertEqual(payload["counts"]["operation_events"], {"activate": 2})

    def test_historical_log_entries_need_not_be_backfilled_with_method_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_healthy_kb(root)
            log = root / "wiki" / "log.md"
            log.write_text(
                log.read_text()
                .replace("- Seven-Blades: Complete\n", "")
                .replace("- Four-Gates: Pass\n", "")
            )

            result = self.run_check(root)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_invalid_or_orphan_dispositions_do_not_pollute_metrics(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_healthy_kb(root)
            log = root / "wiki" / "log.md"
            log.write_text(log.read_text() + "\n- Disposition: Banana\n")

            result = self.run_check(root)
            payload = json.loads(result.stdout)

            self.assertEqual(result.returncode, 1)
            self.assertNotIn("Banana", payload["counts"]["source_dispositions"])
            self.assertIn("orphan-log-field", {item["code"] for item in payload["findings"]})

    def test_log_source_disposition_requires_existing_raw_path(self) -> None:
        for replacement in ("", "- Raw: raw/finance/missing.md\n"):
            with self.subTest(replacement=replacement), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                self.make_healthy_kb(root)
                log = root / "wiki" / "log.md"
                log.write_text(log.read_text().replace("- Raw: raw/finance/report.md\n", replacement))

                result = self.run_check(root)
                payload = json.loads(result.stdout)

                self.assertEqual(result.returncode, 1)
                self.assertEqual(payload["counts"]["source_dispositions"], {})
                self.assertTrue(
                    {"missing-log-raw", "invalid-log-raw"} & {item["code"] for item in payload["findings"]}
                )

    def test_query_or_maintain_disposition_is_invalid_and_never_counted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_healthy_kb(root)
            log = root / "wiki" / "log.md"
            log.write_text(
                "# Knowledge Base Log\n\n"
                "## [2026-07-30] query | Saved answer\n"
                "- Disposition: Banana\n"
                "- Updated: wiki/finance/revenue.md\n"
            )

            result = self.run_check(root)
            payload = json.loads(result.stdout)

            self.assertEqual(result.returncode, 1)
            self.assertEqual(payload["counts"]["source_dispositions"], {})
            self.assertIn("invalid-log-disposition", {item["code"] for item in payload["findings"]})

    def test_reports_invalid_log_date_and_updated_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_healthy_kb(root)
            log = root / "wiki" / "log.md"
            log.write_text(
                log.read_text()
                .replace("[2026-07-30]", "[2026-02-31]")
                .replace("wiki/finance/revenue.md", "../outside.md")
            )

            result = self.run_check(root)
            payload = json.loads(result.stdout)
            codes = {item["code"] for item in payload["findings"]}

            self.assertEqual(result.returncode, 1)
            self.assertIn("invalid-log-date", codes)
            self.assertIn("invalid-log-updated", codes)
            self.assertEqual(payload["counts"]["operation_events"], {})
            self.assertEqual(payload["counts"]["source_dispositions"], {})


if __name__ == "__main__":
    unittest.main()
