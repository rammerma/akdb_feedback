#!/usr/bin/env python3
"""
Haupteinstiegspunkt für das AKDB Feedback Export Tool.
"""

from feedback.feedback import FeedbackData


def main():
    """Hauptfunktion für den Export von Ausländerwesen-Feedback."""
    fd = FeedbackData()
    fd.exportAllAuslaenderwesen()


if __name__ == "__main__":
    main()
