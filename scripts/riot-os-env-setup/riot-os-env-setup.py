from subprocess import run

run(["inet-nm-export", "BOARD", "${NM_BOARD}", "--apply-to-shared"])
run(["inet-nm-export", "BUILD_IN_DOCKER", "1", "--apply-to-shared"])
run(["inet-nm-export", "DEBUG_ADAPTER_ID", "${NM_SERIAL}", "--apply-to-shared"])
run(["inet-nm-export", "PORT", "${NM_PORT}", "--apply-to-shared"])

run(
    [
        "inet-nm-export",
        "PORT",
        "${NM_PORT_1}",
        "--apply-pattern",
        "--boards",
        "esp32-wrover-kit",
    ]
)
