# Two stages (plan-implementation, section 12): the binary is built and tested in
# the Rust image, then copied into a slim runtime image without the toolchain.
# Build context is the repository root, so the probe tests can read schema/.

# rust:1.97.1-slim-bookworm, the toolchain Agave v4.3.2 pins; digest taken 2026-10-26.
FROM rust:1.97.1-slim-bookworm@sha256:2775a09d208ff0d7c1f50490c45b62db929e87ba1dcbc3f2132ac71a704bcdd3 AS build
WORKDIR /src
COPY schema/ schema/
COPY probe/Cargo.toml probe/Cargo.lock probe/
WORKDIR /src/probe
# Dependencies are fetched against a stub main, so a source change reuses this layer.
RUN mkdir src && echo 'fn main() {}' > src/main.rs
# Optional build secret extra_ca: the PEM root of a TLS-inspecting proxy on the build
# machine (an antivirus web shield re-signs crates.io). Only this fetch sees it, it is
# added to the system roots rather than replacing them, and without it nothing changes:
#   docker build --secret id=extra_ca,src=<root.pem> -f probe/Dockerfile -t inside-the-block-probe:local .
RUN --mount=type=secret,id=extra_ca,required=false \
    if [ -s /run/secrets/extra_ca ]; then \
      cat /etc/ssl/certs/ca-certificates.crt /run/secrets/extra_ca > /tmp/roots.pem; \
      export CARGO_HTTP_CAINFO=/tmp/roots.pem; \
    fi; \
    cargo fetch --locked
COPY probe/src/ src/
# A failing test fails the image build (section 11).
RUN cargo test --release --locked --offline && cargo build --release --locked --offline

# debian:bookworm-slim; digest taken 2026-10-26.
FROM debian:bookworm-slim@sha256:7ff6ba31527b9e336162fa061746c366c4b2032f4d2cff2078bea43f78efe3f8
RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates \
 && rm -rf /var/lib/apt/lists/* \
 && useradd --system --uid 10001 --user-group --no-create-home --shell /usr/sbin/nologin itb \
 && mkdir /state \
 && chown 10001:10001 /state
COPY --from=build /src/probe/target/release/itb-probe /usr/local/bin/itb-probe
# The only non-root user of the image runs the only process, so a secret mounted
# with the default 0444 mode is still readable by nobody else (section 11). A named
# volume mounted on /state starts as a copy of this directory, owned by that user.
USER 10001:10001
ENTRYPOINT ["/usr/local/bin/itb-probe"]
