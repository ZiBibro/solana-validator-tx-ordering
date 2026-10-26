# Two stages (plan-implementation, section 12): the binary is built and tested in
# the Rust image, then copied into a slim runtime image without the toolchain.
# Build context is the repository root, so the probe tests can read schema/.

# rust:1.97.1-slim-bookworm, the toolchain Agave v4.3.2 pins; digest taken 2026-10-26.
FROM rust:1.97.1-slim-bookworm@sha256:2775a09d208ff0d7c1f50490c45b62db929e87ba1dcbc3f2132ac71a704bcdd3 AS build
WORKDIR /src
COPY schema/ schema/
COPY probe/Cargo.toml probe/Cargo.lock probe/
COPY probe/src/ probe/src/
WORKDIR /src/probe
# A failing test fails the image build (section 11).
RUN cargo test --release --locked && cargo build --release --locked

# debian:bookworm-slim; digest taken 2026-10-26.
FROM debian:bookworm-slim@sha256:7ff6ba31527b9e336162fa061746c366c4b2032f4d2cff2078bea43f78efe3f8
RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates \
 && rm -rf /var/lib/apt/lists/* \
 && useradd --system --uid 10001 --user-group --no-create-home --shell /usr/sbin/nologin itb
COPY --from=build /src/probe/target/release/itb-probe /usr/local/bin/itb-probe
# The only non-root user of the image runs the only process, so a secret mounted
# with the default 0444 mode is still readable by nobody else (section 11).
USER 10001:10001
ENTRYPOINT ["/usr/local/bin/itb-probe"]
