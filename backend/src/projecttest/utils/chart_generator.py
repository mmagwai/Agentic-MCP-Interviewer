import matplotlib.pyplot as plt
import os


def generate_score_chart(score: int, total: int, path="score_chart.png"):
    correct = score
    wrong = max(total - score, 0)

    labels = ["Correct", "Wrong"]
    values = [correct, wrong]

    plt.figure()
    plt.bar(labels, values)
    plt.title("Interview Performance")
    plt.ylabel("Answers")

    plt.savefig(path)
    plt.close()

    return path
