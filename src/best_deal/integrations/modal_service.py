"""
Modal adapter for the Best Deal fine-tuned pricing model.

Description:
    This module connects the runtime to the existing remotely trained and
    deployed fine-tuned model. It intentionally contains no training code.

Responsibilities:
    - Resolve the remote Modal Pricer class.
    - Expose a small provider-independent pricing method to agents.
"""

from __future__ import annotations

import os


DEFAULT_MODAL_APP = "best-deal-fine-tuned-service"


class ModalPricerService:
    """
    Provide access to the remote Modal fine-tuned price model.

    Returns:
        A configured remote pricing adapter.
    """

    def __init__(self, service_name: str | None = None, class_name: str = "Pricer") -> None:
        """
        Initialize the Modal class reference.

        Args:
            service_name: Deployed Modal application/service name. Defaults to
                BEST_DEAL_MODAL_APP or the app name used by the deployment.
            class_name: Modal class name exposing the price method.

        Returns:
            None.
        """
        try:
            import modal
        except ImportError as exc:
            raise RuntimeError("The 'modal' package is required for SpecialistAgent runtime inference.") from exc
        app_name = service_name or os.getenv("BEST_DEAL_MODAL_APP", DEFAULT_MODAL_APP)
        pricer_class = modal.Cls.from_name(app_name, class_name)
        self.pricer = pricer_class()

    def price(self, description: str) -> float:
        """
        Request a price estimate from Modal.

        Args:
            description: Product description.

        Returns:
            Estimated price in US dollars.
        """
        return float(self.pricer.price.remote(description))
