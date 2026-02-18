from legal_doc_ai.services.classifier import ClassifierService


def test_rule_classifier_contract() -> None:
    svc = ClassifierService()
    label = svc._rule_classify("This agreement between Party A and Party B defines termination clauses.")
    assert label == "contract"


def test_rule_classifier_invoice() -> None:
    svc = ClassifierService()
    label = svc._rule_classify("Invoice amount due is 1200 USD under net 30 payment terms.")
    assert label == "invoice"
