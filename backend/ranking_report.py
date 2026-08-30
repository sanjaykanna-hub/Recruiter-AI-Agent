def generate_ranking_report(ranked_candidates):

    print("\n")
    print("Candidate Ranking Report")
    print("========================")

    if not ranked_candidates:

        print("No candidates found.")
        return

    for position, candidate in enumerate(
        ranked_candidates,
        start=1
    ):

        name = candidate.get(
            "name",
            candidate.get(
                "resume_file",
                "Unknown Candidate"
            )
        )

        print()
        print(
            f"{position}. {name}"
        )

        print(
            f"   Final Score: "
            f"{candidate.get('final_score', 0):.2f}%"
        )

        # --------------------------------
        # Skill scores
        # --------------------------------

        print()

        print(
            f"   Required Skill Score: "
            f"{candidate.get('required_skill_score', 0):.2f}%"
        )

        print(
            f"   Preferred Skill Score: "
            f"{candidate.get('preferred_skill_score', 0):.2f}%"
        )

        print(
            f"   Overall Skill Score: "
            f"{candidate.get('overall_skill_score', 0):.2f}%"
        )

        print()

        print(
            f"   Keyword Baseline: "
            f"{candidate.get('keyword_skill_score', 0):.2f}%"
        )

        print(
            f"   Verified Evidence Score: "
            f"{candidate.get('semantic_evidence_score', 0):.2f}%"
        )

        print(
            f"   Hybrid Skill Score: "
            f"{candidate.get('hybrid_skill_score', 0):.2f}%"
        )

        # --------------------------------
        # Required skills
        # --------------------------------

        print()

        print(
            "   Matched Required Skills:"
        )

        matched_required = candidate.get(
            "matched_required",
            []
        )

        if matched_required:

            for skill in matched_required:

                print(
                    f"   - {skill}"
                )

        else:

            print(
                "   - None"
            )

        # --------------------------------
        # Preferred skills
        # --------------------------------

        print()

        print(
            "   Matched Preferred Skills:"
        )

        matched_preferred = candidate.get(
            "matched_preferred",
            []
        )

        if matched_preferred:

            for skill in matched_preferred:

                print(
                    f"   - {skill}"
                )

        else:

            print(
                "   - None"
            )

        # --------------------------------
        # Missing required
        # --------------------------------

        print()

        print(
            "   Missing Required Skills:"
        )

        missing_skills = candidate.get(
            "missing_skills",
            []
        )

        if missing_skills:

            for skill in missing_skills:

                print(
                    f"   - {skill}"
                )

        else:

            print(
                "   - None"
            )

        # --------------------------------
        # Experience
        # --------------------------------

        print()

        print(
            f"   Experience: "
            f"{candidate.get('experience', 0)} years"
        )

        print(
            f"   Experience Score: "
            f"{candidate.get('experience_score', 0)}"
        )

        # --------------------------------
        # Education
        # --------------------------------

        print(
            f"   Education Score: "
            f"{candidate.get('education_score', 0)}"
        )

        # --------------------------------
        # VERIFIED RAG EVIDENCE
        # --------------------------------

        print()

        print(
            "   Verified Evidence:"
        )

        evidence = candidate.get(
            "evidence",
            []
        )

        if not evidence:

            print(
                "   - No evidence available"
            )

        else:

            for item in evidence:

                skill = item.get(
                    "skill",
                    "Unknown"
                )

                verified = item.get(
                    "verified",
                    False
                )

                if verified:

                    evidence_data = (
                        item.get(
                            "evidence"
                        )
                    )

                    if evidence_data:

                        section = (
                            evidence_data.get(
                                "section",
                                "Unknown"
                            )
                        )

                        score = (
                            evidence_data.get(
                                "score",
                                0
                            )
                        )

                        print(
                            f"   - {skill}: "
                            f"VERIFIED"
                        )

                        print(
                            f"     Section: "
                            f"{section}"
                        )

                        print(
                            f"     Semantic Score: "
                            f"{score:.2f}%"
                        )

                    else:

                        print(
                            f"   - {skill}: "
                            f"VERIFIED"
                        )

                else:

                    print(
                        f"   - {skill}: "
                        f"NOT VERIFIED"
                    )

        print()

        print(
            "-" * 50
        )


if __name__ == "__main__":

    print(
        "ranking_report.py is a reporting module."
    )

    print(
        "Run batch_evaluator.py to generate "
        "the candidate ranking report."
    )