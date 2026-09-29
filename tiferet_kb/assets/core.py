"""tiferet_kb Assets Core"""

# *** constants

# ** constant: visibility_public
VISIBILITY_PUBLIC = 'public'

# ** constant: visibility_private
VISIBILITY_PRIVATE = 'private'

# ** constant: visibility_restricted
VISIBILITY_RESTRICTED = 'restricted'

# ** constant: visibilities
VISIBILITIES = (
    VISIBILITY_PUBLIC,
    VISIBILITY_PRIVATE,
    VISIBILITY_RESTRICTED,
)

# *** constants (document link)

# ** constant: document_link_references
DOCUMENT_LINK_REFERENCES = 'references'

# ** constant: document_link_supersedes
DOCUMENT_LINK_SUPERSEDES = 'supersedes'

# ** constant: document_link_related_to
DOCUMENT_LINK_RELATED_TO = 'related_to'

# ** constant: document_link_outgoing
DOCUMENT_LINK_OUTGOING = 'outgoing'

# ** constant: document_link_incoming
DOCUMENT_LINK_INCOMING = 'incoming'

# ** constant: document_link_both
DOCUMENT_LINK_BOTH = 'both'
