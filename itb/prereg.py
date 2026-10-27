"""Analysis constants fixed before the pilot (section 10).

The prereg manifest lists the SHA-256 of this file next to the plan and the
seed table, and the memo transaction puts the manifest hash on chain before the
first live burst. A change here after that moment shows up as a hash mismatch
in verify.
"""

CLASSES = ("AgaveBam", "JitoLabs", "HarmonicAgave", "HarmonicFiredancer",
           "Firedancer", "FireBAM", "Rakurai", "Agave")

# Section 1: each fork with a builder against the code base it stands on.
PAIRS = (("AgaveBam", "JitoLabs"), ("FireBAM", "Firedancer"),
         ("HarmonicAgave", "Agave"), ("HarmonicFiredancer", "Firedancer"))

ARMS = ("independent", "shared", "equal_fee", "denominator")
TIMINGS = ("pre300", "slot2")

# tau = 1 - 2 * violation share for pairs without ties, so delta 0.2 calls a rule
# invisible once its violation share is shown to lie within 0.4 to 0.6.
DELTA_CLASS = 0.2
# Class difference of the same tau inside a pair, same scale.
DELTA_PAIR = 0.2

# Minimum-burst formula: smallest B with
#   (t_{B-1, 1 - alpha_e} + t_{B-1, (1 + POWER_PER_TAU) / 2}) * sigma / sqrt(B) <= DELTA_CLASS
# where alpha_e is the first Holm threshold of the equivalence family and sigma
# the residual sd of burst tau in the additive class + cell model of the pilot.
# "No rule visible" needs two taus, so 0.9 each keeps the joint chance near 0.8.
POWER_PER_TAU = 0.9

# Moment condition bands, ms from the target as (low, high): an estimated arrival
# (send offset from the first slot start plus half the RTT) inside the band
# counts as the condition; bursts outside go to a separate group. Both bands
# run 100 ms either side of the target; the pair form lets one side move
# without touching the other.
TIMING_TARGET_MS = {"pre300": -300.0, "slot2": None}  # slot2 target = start of slot 2, analyze.slot2_ms
TIMING_BAND_MS = {"pre300": (-100.0, 100.0), "slot2": (-100.0, 100.0)}

# Section 5.1: slot clock guard. getSlot at processed commitment this many slots
# or more ahead of the slot the clock gave for the same moment means the burst
# was aimed late; the probe skips such a burst, and analyze keeps any burst row
# with that lag out of the verdict. Rows of schema version 1 predate the guard:
# for them the confirmed blockhash, fetched BLOCKHASH_LEAD_SLOTS before the
# window by the clock, must come from a slot before that point.
CLOCK_LAG_SKIP_SLOTS = 2
BLOCKHASH_LEAD_SLOTS = 6

# Section 3: default QUIC port of the Jito relayer.
RELAYER_PORT = 11228

# Label permutation tests with more than 20 strata.
LABEL_TEST_B = 19999
LABEL_TEST_SEED = "itb-prereg-label-v1"
