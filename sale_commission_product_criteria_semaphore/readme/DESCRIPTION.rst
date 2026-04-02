This module extends ``sale_commission_product_criteria`` so commission rules can
also be filtered by semaphore status.

With it, you can keep the usual product/category-based rules and add more
specific percentages for lines marked as green, yellow or red in
``sale_semaphore``. Generic rules without semaphore remain valid as a fallback.
