def rank_candidates(candidates):
    return sorted(
        candidates,
        key=lambda candidate: candidate["final_score"],
        reverse=True
    )


if __name__ == "__main__":

    candidates = [
        {
            "name": "Candidate A",
            "final_score": 82.5
        },
        {
            "name": "Candidate B",
            "final_score": 76.2
        },
        {
            "name": "Candidate C",
            "final_score": 91.4
        },
        {
            "name": "Candidate D",
            "final_score": 68.7
        }
    ]

    ranked_candidates = rank_candidates(candidates)

    print("\nCandidate Ranking")
    print("-----------------")

    for position, candidate in enumerate(
        ranked_candidates,
        start=1
    ):
        print(
            f"{position}. "
            f"{candidate['name']} - "
            f"{candidate['final_score']}%"
        )