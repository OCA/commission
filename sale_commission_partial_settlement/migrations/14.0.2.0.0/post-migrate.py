import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


def recompute_partial_commission_forecast(env):
    """
    Recompute forecast for all partial commissions
    """
    _logger.info(
        "Computing partial commission forecast for all invoices. "
        "This may take some time..."
    )
    limit = 5000
    offset = 0
    while True:
        aila = env["account.invoice.line.agent"].search([], limit=limit, offset=offset)
        if not aila:
            break
        offset += limit
        aila._compute_invoice_line_agent_partial_ids()
        while env.all.tocompute:
            aila.flush()
        aila.invalidate_cache()  # avoid MemoryError
        _logger.info(
            "%(offset)s invoice commission lines computed!" % {"offset": str(offset)}
        )
    _logger.info("Computation of partial commission forecast completed!")


@openupgrade.migrate()
def migrate(env, version):
    recompute_partial_commission_forecast(env)
