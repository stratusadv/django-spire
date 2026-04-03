# Prototype of refactored REST client architecture
#
# Key changes from current implementation:
# 1. Separated transport layer (HTTP concerns) from client (business logic)
# 2. QuerySet receives a fetcher callable, not a client reference
# 3. Support for result extractors (paginated/nested API responses)
# 4. Cleaner separation of concerns
