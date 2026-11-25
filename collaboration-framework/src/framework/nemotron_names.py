"""The Nemotron name translator (Ben's ruling, 2026-11-24):
a SEPARATE translator for the NVIDIA route, standing beside
the framework's canonical tool names — never inside them.

Inside the framework everything keeps the canonical dotted
names (container.exec, sandbox.*, probe.lookup): the record,
the doorway's grants, the catalogue and the checker all speak
them, on every route. But the NVIDIA route's provider
validates the function names it is offered against a strict
alphabet — its own words, preserved in the first Nemotron
run's record (live-demo/demo-nemotron1, the ASSEMBLY_PROBED
trials, HTTP 400):

    "Validation: Function at index 0 has an invalid name:
    \"probe.lookup\". Only a-z, A-Z, 0-9, underscores, and
    dashes are allowed."

A dotted name is refused before the model ever sees the
request. Ben's ruling, in his words: "we create a separate
translater for nemotron. he says the dot, but the - is what
is read." The canonical name is what the framework says; the
dash form is what this route's provider reads. So on this
route only, a tool's name crosses the wire with each dot
replaced by a dash (container.exec travels as
container-exec), and an emitted dash name is translated
back to its canonical name at the adapter's extraction,
before classification — the translation record keeping both
names visible.

The translator is an exact bijection built from the names
actually offered, never free string munging at a call site:

- outbound, a canonical name maps to its one wire form;
- inbound, a wire name maps back ONLY where it stands in
  the map. A name that is not a wire form of an offered
  tool is NOT guessed back — no dash-to-dot rewriting is
  ever applied to an emitted name; it stands exactly as
  emitted, for the closed-world catalogue determination
  to refuse like any unknown tool.

Construction verifies the bijection over the names it is
given: two canonical names mapping to one wire form, a
wire form that collides with a canonical name in the set,
or a duplicated canonical name each refuse construction —
a translator that cannot be reversed exactly is not built.

The route is the assembly's own recorded route — the value
the run's ASSEMBLY_PROBED act carries, supplied by the
driver that recorded it. Nothing here, and nothing that
consults this module, infers a route from a model name
string. Every other route gets no translator, and its
names travel exactly as they stand.
"""

# The route value the assembly record carries for the
# NVIDIA route (the ASSEMBLY_PROBED payload's `route`,
# as the drivers record it). This module's translation
# exists for this route alone.
NVIDIA_ROUTE = "nvidia"

# The framework's standing tool vocabulary, canonical
# forms: the worker-facing registry's tools and the probe
# stage's synthetic pair. The translator witness
# (tests/unit/test_nemotron_names.py) verifies the
# bijection over exactly this set.
VOCABULARY = (
    "container.exec",
    "sandbox.list",
    "sandbox.read",
    "sandbox.read_range",
    "sandbox.search",
    "sandbox.write",
    "probe.lookup",
    "probe.note",
)


def wire_form(canonical):
    """One canonical name's wire form on this route: each
    dot a dash. The provider's allowed alphabet (letters,
    digits, underscores, dashes) admits the result for
    every name in the standing vocabulary."""
    return canonical.replace(".", "-")


class NameTranslator:
    """The exact bijection between one offered set's
    canonical names and their wire forms. Constructed
    from the canonical names themselves; construction
    refuses a set over which the mapping is not exactly
    reversible."""

    def __init__(self, canonical_names):
        canonical_names = list(canonical_names)
        self._to_wire = {}
        self._to_canonical = {}
        for name in canonical_names:
            if not isinstance(name, str) or not name:
                raise ValueError(
                    "a tool name in the offered set is not "
                    f"a non-empty string: {name!r}")
            if name in self._to_wire:
                raise ValueError(
                    f"the canonical name {name!r} stands "
                    f"twice in the offered set; the "
                    f"bijection is built over distinct "
                    f"names")
            wire = wire_form(name)
            if wire in self._to_canonical:
                raise ValueError(
                    f"the canonical names {name!r} and "
                    f"{self._to_canonical[wire]!r} map to "
                    f"the one wire form {wire!r}; the "
                    f"translation would not reverse "
                    f"exactly")
            if wire in canonical_names and wire != name:
                raise ValueError(
                    f"the wire form {wire!r} of {name!r} "
                    f"collides with a canonical name in "
                    f"the offered set; an emitted name "
                    f"could not be told apart from its "
                    f"translation")
            self._to_wire[name] = wire
            self._to_canonical[wire] = name

    @property
    def canonical_names(self):
        return tuple(self._to_wire)

    @property
    def wire_names(self):
        return tuple(self._to_canonical)

    def to_wire(self, canonical):
        """The wire form of a canonical name in the map,
        or None where the name was not offered — an
        unoffered name has no wire form and is never
        invented one."""
        return self._to_wire.get(canonical)

    def to_canonical(self, wire):
        """The canonical name a wire name translates back
        to, or None where the emitted name is not a wire
        form in the map. None is the not-guessed-back
        rule: the name stands as emitted, unknown to the
        translation, for the catalogue's closed-world
        determination to refuse."""
        return self._to_canonical.get(wire)


def translator_for_route(route, canonical_names):
    """The translator for an assembly's recorded route
    over the given canonical names, or None: translation
    exists only on the NVIDIA route; every other route —
    and an unrecorded route — gets none, and its names
    travel exactly as they stand."""
    if route != NVIDIA_ROUTE:
        return None
    return NameTranslator(canonical_names)


def translator_for_package(route, package):
    """The translator for a wake package on the given
    route: built over the package's own catalogue names —
    the names the package offers, derived by the
    catalogue's own name rule (an entry's `tool`, or its
    `name`), each once, in catalogue order. None where
    the route carries no translation, or the package
    offers no tools."""
    if route != NVIDIA_ROUTE:
        return None
    tools = package.get("tools") \
        if isinstance(package, dict) else None
    names = []
    for entry in tools or []:
        if not isinstance(entry, dict):
            continue
        name = entry.get("tool") or entry.get("name")
        if isinstance(name, str) and name \
                and name not in names:
            names.append(name)
    if not names:
        return None
    return NameTranslator(names)
