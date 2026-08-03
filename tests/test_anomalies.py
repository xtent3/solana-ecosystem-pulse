import unittest

from solpulse.anomalies import detect_anomalies


class DetectAnomaliesTests(unittest.TestCase):
    def test_flags_low_tps_and_high_delinquent_stake(self):
        metrics = {"tps": 650.0, "delinquent_stake_pct": 6.25}

        alerts = detect_anomalies(metrics, min_tps=1000, max_delinquent_stake_pct=5)

        self.assertEqual(
            alerts,
            [
                {
                    "code": "low_tps",
                    "severity": "warning",
                    "message": "Observed TPS 650.0 is below threshold 1000.0.",
                },
                {
                    "code": "high_delinquent_stake",
                    "severity": "critical",
                    "message": "Delinquent stake 6.25% exceeds threshold 5.0%.",
                },
            ],
        )

    def test_reports_healthy_when_thresholds_are_not_crossed(self):
        metrics = {"tps": 2500.0, "delinquent_stake_pct": 1.2}

        self.assertEqual(detect_anomalies(metrics), [])


if __name__ == "__main__":
    unittest.main()
