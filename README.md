# Boot matrix results

Commit `853abe28630c`, run [2](https://github.com/iwanicki92/drtm-tests/actions/runs/35776046177), finished 2026-09-22 19:51:33.
QEMU bundle `drtm-11.1.1-1` (11.1.1 (v11.1.1-43-gff57ce2273-dirty)), swtpm 0.7.3.

Rows are the GRUB entries the suite boots, named as their fixtures
in `tests/conftest.py`, columns the releases. ✅ every test of the
entry passed, ❌ one failed, - nothing ran. A mark says what the
boot did, and the notes under the table what the suite expected of it.

## Classic launch, TPM with SHA-1 and SHA-256

| Entry                 | v0.5.2 | v0.5.3-rc1 |
|-----------------------|--------|------------|
| `xen_efi_launch`      | -      | ✅          |
| `xen_efi`             | -      | ✅          |
| `xen_mb2_launch`      | -      | ✅          |
| `linux_launch`        | -      | ❌          |
| `linux_legacy_launch` | -      | ✅          |
| `linux_alt_launch`    | -      | ✅          |
| `linux`               | -      | ✅          |

- No results for `v0.5.2`.
- `v0.5.3-rc1`: 67 passed, 5 xfailed.
    - `linux_launch` expected: panics in check_timer: SKL entered startup_32, GIF never set

<details>
<summary>Every test</summary>

| Test                                                                                              | v0.5.2 | v0.5.3-rc1 |
|---------------------------------------------------------------------------------------------------|--------|------------|
| `tests/test_eventlog.py::test_the_xen_log_is_the_skls_events_then_xens`                           | -      | passed     |
| `tests/test_eventlog.py::test_the_header_declares_the_banks_in_its_order`                         | -      | passed     |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[17-sha256]`                         | -      | passed     |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[17-sha1]`                           | -      | passed     |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[18-sha256]`                         | -      | passed     |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[18-sha1]`                           | -      | passed     |
| `tests/test_eventlog.py::test_the_linux_log_has_the_kernels_tags`                                 | -      | passed     |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[17-sha256]` | -      | passed     |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[17-sha1]`   | -      | passed     |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[18-sha256]` | -      | passed     |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[18-sha1]`   | -      | passed     |
| `tests/test_eventlog.py::test_the_zero_tail_of_the_log_region_is_not_an_event`                    | -      | passed     |
| `tests/test_eventlog.py::test_an_event_without_the_bank_leaves_that_banks_replay_alone`           | -      | passed     |
| `tests/test_eventlog.py::test_an_empty_or_foreign_buffer_is_refused`                              | -      | passed     |
| `tests/test_grubcfg.py::test_entries_keep_their_commands_in_order_without_the_noise`              | -      | passed     |
| `tests/test_grubcfg.py::test_the_parameter_lands_on_the_kernel_line_alone`                        | -      | passed     |
| `tests/test_grubcfg.py::test_an_entry_without_a_kernel_line_is_refused`                           | -      | passed     |
| `tests/test_grubcfg.py::test_the_boot_partition_is_the_efi_system_partition`                      | -      | passed     |
| `tests/test_grubcfg.py::test_a_disk_without_one_is_refused`                                       | -      | passed     |
| `tests/test_linux.py::test_launch_is_recorded_by_the_platform`                                    | -      | xfailed    |
| `tests/test_linux.py::test_launch_is_seen_by_linux`                                               | -      | xfailed    |
| `tests/test_linux.py::test_launch_brings_the_iommu_up`                                            | -      | xfailed    |
| `tests/test_linux.py::test_launch_log_replays_to_the_pcrs`                                        | -      | xfailed    |
| `tests/test_linux.py::test_launch_log_declares_the_tpms_banks`                                    | -      | xfailed    |
| `tests/test_linux.py::test_legacy_launch_is_recorded_by_the_platform`                             | -      | passed     |
| `tests/test_linux.py::test_legacy_launch_is_seen_by_linux`                                        | -      | passed     |
| `tests/test_linux.py::test_legacy_launch_brings_the_iommu_up`                                     | -      | passed     |
| `tests/test_linux.py::test_legacy_launch_log_replays_to_the_pcrs`                                 | -      | passed     |
| `tests/test_linux.py::test_legacy_launch_log_declares_the_tpms_banks`                             | -      | passed     |
| `tests/test_linux.py::test_alt_launch_is_recorded_by_the_platform`                                | -      | passed     |
| `tests/test_linux.py::test_alt_launch_is_seen_by_linux`                                           | -      | passed     |
| `tests/test_linux.py::test_alt_launch_log_replays_to_the_pcrs`                                    | -      | passed     |
| `tests/test_linux.py::test_alt_launch_log_declares_the_tpms_banks`                                | -      | passed     |
| `tests/test_linux.py::test_the_command_line_is_measured_into_pcr_18_alone`                        | -      | passed     |
| `tests/test_linux.py::test_normal_boot_launches_nothing`                                          | -      | passed     |
| `tests/test_matrix.py::test_the_workflow_gets_every_release_under_every_configuration`            | -      | passed     |
| `tests/test_matrix.py::test_a_selection_of_releases_is_kept_in_the_order_given`                   | -      | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env0-classic]`                | -      | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env1-psp]`                    | -      | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env2-sha256]`                 | -      | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env3-psp-sha256]`             | -      | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env4-sha384]`                 | -      | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env5-psp]`                    | -      | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env6-None]`                   | -      | passed     |
| `tests/test_matrix.py::test_a_cell_replaces_the_configuration_variables_and_the_local_image`      | -      | passed     |
| `tests/test_menu.py::test_titles_come_out_in_menu_order_once_each`                                | -      | passed     |
| `tests/test_menu.py::test_the_image_lists_every_entry_this_suite_knows`                           | -      | passed     |
| `tests/test_qemu_binary.py::test_the_configured_binary_is_ours`                                   | -      | passed     |
| `tests/test_qemu_binary.py::test_a_refused_option_is_reported`                                    | -      | passed     |
| `tests/test_qemu_binary.py::test_a_warning_named_in_rejects_is_reported`                          | -      | passed     |
| `tests/test_qemu_binary.py::test_a_missing_binary_is_reported`                                    | -      | passed     |
| `tests/test_report.py::test_a_cell_says_what_the_boot_did`                                        | -      | passed     |
| `tests/test_report.py::test_the_notes_say_what_was_expected`                                      | -      | passed     |
| `tests/test_report.py::test_a_release_without_results_is_a_missing_column`                        | -      | passed     |
| `tests/test_report.py::test_the_full_table_has_every_test_and_the_parser_ones_only_there`         | -      | passed     |
| `tests/test_report.py::test_the_sections_and_columns_follow_the_matrix_order`                     | -      | passed     |
| `tests/test_report.py::test_the_header_names_the_commit_the_run_and_the_tools`                    | -      | passed     |
| `tests/test_report.py::test_a_badge_is_green_only_when_every_configuration_passed`                | -      | passed     |
| `tests/test_report.py::test_a_missing_configuration_alone_is_red_too`                             | -      | passed     |
| `tests/test_report.py::test_a_hand_made_session_gets_a_section_of_its_own`                        | -      | passed     |
| `tests/test_report.py::test_main_reads_a_tree_of_results_and_writes_the_page_and_badges`          | -      | passed     |
| `tests/test_xen.py::test_efi_launch_is_recorded_by_the_platform`                                  | -      | passed     |
| `tests/test_xen.py::test_efi_launch_is_seen_by_xen`                                               | -      | passed     |
| `tests/test_xen.py::test_efi_launch_brings_the_iommu_up`                                          | -      | passed     |
| `tests/test_xen.py::test_efi_launch_log_replays_to_the_pcrs`                                      | -      | passed     |
| `tests/test_xen.py::test_efi_launch_log_declares_the_tpms_banks`                                  | -      | passed     |
| `tests/test_xen.py::test_efi_normal_boot_launches_nothing`                                        | -      | passed     |
| `tests/test_xen.py::test_mb2_launch_is_recorded_by_the_platform`                                  | -      | passed     |
| `tests/test_xen.py::test_mb2_launch_is_seen_by_xen`                                               | -      | passed     |
| `tests/test_xen.py::test_mb2_launch_brings_the_iommu_up`                                          | -      | passed     |
| `tests/test_xen.py::test_mb2_launch_log_replays_to_the_pcrs`                                      | -      | passed     |
| `tests/test_xen.py::test_mb2_launch_log_declares_the_tpms_banks`                                  | -      | passed     |

</details>

## PSP DRTM service on, SHA-256 alone

| Entry                 | v0.5.2 | v0.5.3-rc1 |
|-----------------------|--------|------------|
| `xen_efi_launch`      | ❌      | -          |
| `xen_efi`             | ✅      | -          |
| `xen_mb2_launch`      | ❌      | -          |
| `linux_launch`        | ❌      | -          |
| `linux_legacy_launch` | ❌      | -          |
| `linux_alt_launch`    | ❌      | -          |
| `linux`               | ✅      | -          |

- `v0.5.2`: 49 passed, 23 xfailed.
    - `linux_launch` expected: classic SKL: the kernel's extend fails at a locked locality, it panics
    - `linux_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has
    - `linux_legacy_launch` expected: classic SKL: the kernel's extend fails at a locked locality, it panics
    - `linux_legacy_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has
    - `linux_alt_launch` expected: classic SKL: the kernel's extend fails at a locked locality, it panics
    - `linux_alt_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has
    - `xen_efi_launch` expected: classic SKL: no LAUNCH, so the PSP's locality locks stay on the TPM
    - `xen_efi_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has
    - `xen_mb2_launch` expected: classic SKL: no LAUNCH, so the PSP's locality locks stay on the TPM
    - `xen_mb2_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has
- No results for `v0.5.3-rc1`.

<details>
<summary>Every test</summary>

| Test                                                                                              | v0.5.2  | v0.5.3-rc1 |
|---------------------------------------------------------------------------------------------------|---------|------------|
| `tests/test_eventlog.py::test_the_xen_log_is_the_skls_events_then_xens`                           | passed  | -          |
| `tests/test_eventlog.py::test_the_header_declares_the_banks_in_its_order`                         | passed  | -          |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[17-sha256]`                         | passed  | -          |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[17-sha1]`                           | passed  | -          |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[18-sha256]`                         | passed  | -          |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[18-sha1]`                           | passed  | -          |
| `tests/test_eventlog.py::test_the_linux_log_has_the_kernels_tags`                                 | passed  | -          |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[17-sha256]` | passed  | -          |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[17-sha1]`   | passed  | -          |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[18-sha256]` | passed  | -          |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[18-sha1]`   | passed  | -          |
| `tests/test_eventlog.py::test_the_zero_tail_of_the_log_region_is_not_an_event`                    | passed  | -          |
| `tests/test_eventlog.py::test_an_event_without_the_bank_leaves_that_banks_replay_alone`           | passed  | -          |
| `tests/test_eventlog.py::test_an_empty_or_foreign_buffer_is_refused`                              | passed  | -          |
| `tests/test_grubcfg.py::test_entries_keep_their_commands_in_order_without_the_noise`              | passed  | -          |
| `tests/test_grubcfg.py::test_the_parameter_lands_on_the_kernel_line_alone`                        | passed  | -          |
| `tests/test_grubcfg.py::test_an_entry_without_a_kernel_line_is_refused`                           | passed  | -          |
| `tests/test_grubcfg.py::test_the_boot_partition_is_the_efi_system_partition`                      | passed  | -          |
| `tests/test_grubcfg.py::test_a_disk_without_one_is_refused`                                       | passed  | -          |
| `tests/test_linux.py::test_launch_is_recorded_by_the_platform`                                    | xfailed | -          |
| `tests/test_linux.py::test_launch_is_seen_by_linux`                                               | xfailed | -          |
| `tests/test_linux.py::test_launch_brings_the_iommu_up`                                            | xfailed | -          |
| `tests/test_linux.py::test_launch_log_replays_to_the_pcrs`                                        | xfailed | -          |
| `tests/test_linux.py::test_launch_log_declares_the_tpms_banks`                                    | xfailed | -          |
| `tests/test_linux.py::test_legacy_launch_is_recorded_by_the_platform`                             | xfailed | -          |
| `tests/test_linux.py::test_legacy_launch_is_seen_by_linux`                                        | xfailed | -          |
| `tests/test_linux.py::test_legacy_launch_brings_the_iommu_up`                                     | xfailed | -          |
| `tests/test_linux.py::test_legacy_launch_log_replays_to_the_pcrs`                                 | xfailed | -          |
| `tests/test_linux.py::test_legacy_launch_log_declares_the_tpms_banks`                             | xfailed | -          |
| `tests/test_linux.py::test_alt_launch_is_recorded_by_the_platform`                                | xfailed | -          |
| `tests/test_linux.py::test_alt_launch_is_seen_by_linux`                                           | xfailed | -          |
| `tests/test_linux.py::test_alt_launch_log_replays_to_the_pcrs`                                    | xfailed | -          |
| `tests/test_linux.py::test_alt_launch_log_declares_the_tpms_banks`                                | xfailed | -          |
| `tests/test_linux.py::test_the_command_line_is_measured_into_pcr_18_alone`                        | xfailed | -          |
| `tests/test_linux.py::test_normal_boot_launches_nothing`                                          | passed  | -          |
| `tests/test_matrix.py::test_the_workflow_gets_every_release_under_every_configuration`            | passed  | -          |
| `tests/test_matrix.py::test_a_selection_of_releases_is_kept_in_the_order_given`                   | passed  | -          |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env0-classic]`                | passed  | -          |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env1-psp]`                    | passed  | -          |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env2-sha256]`                 | passed  | -          |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env3-psp-sha256]`             | passed  | -          |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env4-sha384]`                 | passed  | -          |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env5-psp]`                    | passed  | -          |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env6-None]`                   | passed  | -          |
| `tests/test_matrix.py::test_a_cell_replaces_the_configuration_variables_and_the_local_image`      | passed  | -          |
| `tests/test_menu.py::test_titles_come_out_in_menu_order_once_each`                                | passed  | -          |
| `tests/test_menu.py::test_the_image_lists_every_entry_this_suite_knows`                           | passed  | -          |
| `tests/test_qemu_binary.py::test_the_configured_binary_is_ours`                                   | passed  | -          |
| `tests/test_qemu_binary.py::test_a_refused_option_is_reported`                                    | passed  | -          |
| `tests/test_qemu_binary.py::test_a_warning_named_in_rejects_is_reported`                          | passed  | -          |
| `tests/test_qemu_binary.py::test_a_missing_binary_is_reported`                                    | passed  | -          |
| `tests/test_report.py::test_a_cell_says_what_the_boot_did`                                        | passed  | -          |
| `tests/test_report.py::test_the_notes_say_what_was_expected`                                      | passed  | -          |
| `tests/test_report.py::test_a_release_without_results_is_a_missing_column`                        | passed  | -          |
| `tests/test_report.py::test_the_full_table_has_every_test_and_the_parser_ones_only_there`         | passed  | -          |
| `tests/test_report.py::test_the_sections_and_columns_follow_the_matrix_order`                     | passed  | -          |
| `tests/test_report.py::test_the_header_names_the_commit_the_run_and_the_tools`                    | passed  | -          |
| `tests/test_report.py::test_a_badge_is_green_only_when_every_configuration_passed`                | passed  | -          |
| `tests/test_report.py::test_a_missing_configuration_alone_is_red_too`                             | passed  | -          |
| `tests/test_report.py::test_a_hand_made_session_gets_a_section_of_its_own`                        | passed  | -          |
| `tests/test_report.py::test_main_reads_a_tree_of_results_and_writes_the_page_and_badges`          | passed  | -          |
| `tests/test_xen.py::test_efi_launch_is_recorded_by_the_platform`                                  | xfailed | -          |
| `tests/test_xen.py::test_efi_launch_is_seen_by_xen`                                               | xfailed | -          |
| `tests/test_xen.py::test_efi_launch_brings_the_iommu_up`                                          | passed  | -          |
| `tests/test_xen.py::test_efi_launch_log_replays_to_the_pcrs`                                      | xfailed | -          |
| `tests/test_xen.py::test_efi_launch_log_declares_the_tpms_banks`                                  | xfailed | -          |
| `tests/test_xen.py::test_efi_normal_boot_launches_nothing`                                        | passed  | -          |
| `tests/test_xen.py::test_mb2_launch_is_recorded_by_the_platform`                                  | xfailed | -          |
| `tests/test_xen.py::test_mb2_launch_is_seen_by_xen`                                               | xfailed | -          |
| `tests/test_xen.py::test_mb2_launch_brings_the_iommu_up`                                          | passed  | -          |
| `tests/test_xen.py::test_mb2_launch_log_replays_to_the_pcrs`                                      | xfailed | -          |
| `tests/test_xen.py::test_mb2_launch_log_declares_the_tpms_banks`                                  | xfailed | -          |

</details>

## TPM with SHA-384 on top

| Entry                 | v0.5.2 | v0.5.3-rc1 |
|-----------------------|--------|------------|
| `xen_efi_launch`      | ❌      | ❌          |
| `xen_efi`             | ✅      | ✅          |
| `xen_mb2_launch`      | ❌      | ❌          |
| `linux_launch`        | ❌      | ❌          |
| `linux_legacy_launch` | ❌      | ❌          |
| `linux_alt_launch`    | ❌      | ❌          |
| `linux`               | ✅      | ✅          |

- `v0.5.2`: 54 passed, 18 xfailed.
    - `linux_launch` expected: panics in check_timer: SKL entered startup_32, GIF never set
    - `linux_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has
    - `linux_legacy_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has
    - `linux_alt_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has
    - `xen_efi_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has
    - `xen_mb2_launch` expected: the upstream Xen copies the MBI's digests for SHA-1 and SHA-256 alone
    - `xen_mb2_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has
- `v0.5.3-rc1`: 54 passed, 18 xfailed.
    - `linux_launch` expected: panics in check_timer: SKL entered startup_32, GIF never set
    - `linux_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has
    - `linux_legacy_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has
    - `linux_alt_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has
    - `xen_efi_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has
    - `xen_mb2_launch` expected: the upstream Xen copies the MBI's digests for SHA-1 and SHA-256 alone
    - `xen_mb2_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has

<details>
<summary>Every test</summary>

| Test                                                                                              | v0.5.2  | v0.5.3-rc1 |
|---------------------------------------------------------------------------------------------------|---------|------------|
| `tests/test_eventlog.py::test_the_xen_log_is_the_skls_events_then_xens`                           | passed  | passed     |
| `tests/test_eventlog.py::test_the_header_declares_the_banks_in_its_order`                         | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[17-sha256]`                         | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[17-sha1]`                           | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[18-sha256]`                         | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[18-sha1]`                           | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_has_the_kernels_tags`                                 | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[17-sha256]` | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[17-sha1]`   | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[18-sha256]` | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[18-sha1]`   | passed  | passed     |
| `tests/test_eventlog.py::test_the_zero_tail_of_the_log_region_is_not_an_event`                    | passed  | passed     |
| `tests/test_eventlog.py::test_an_event_without_the_bank_leaves_that_banks_replay_alone`           | passed  | passed     |
| `tests/test_eventlog.py::test_an_empty_or_foreign_buffer_is_refused`                              | passed  | passed     |
| `tests/test_grubcfg.py::test_entries_keep_their_commands_in_order_without_the_noise`              | passed  | passed     |
| `tests/test_grubcfg.py::test_the_parameter_lands_on_the_kernel_line_alone`                        | passed  | passed     |
| `tests/test_grubcfg.py::test_an_entry_without_a_kernel_line_is_refused`                           | passed  | passed     |
| `tests/test_grubcfg.py::test_the_boot_partition_is_the_efi_system_partition`                      | passed  | passed     |
| `tests/test_grubcfg.py::test_a_disk_without_one_is_refused`                                       | passed  | passed     |
| `tests/test_linux.py::test_launch_is_recorded_by_the_platform`                                    | xfailed | xfailed    |
| `tests/test_linux.py::test_launch_is_seen_by_linux`                                               | xfailed | xfailed    |
| `tests/test_linux.py::test_launch_brings_the_iommu_up`                                            | xfailed | xfailed    |
| `tests/test_linux.py::test_launch_log_replays_to_the_pcrs`                                        | xfailed | xfailed    |
| `tests/test_linux.py::test_launch_log_declares_the_tpms_banks`                                    | xfailed | xfailed    |
| `tests/test_linux.py::test_legacy_launch_is_recorded_by_the_platform`                             | xfailed | xfailed    |
| `tests/test_linux.py::test_legacy_launch_is_seen_by_linux`                                        | xfailed | xfailed    |
| `tests/test_linux.py::test_legacy_launch_brings_the_iommu_up`                                     | xfailed | xfailed    |
| `tests/test_linux.py::test_legacy_launch_log_replays_to_the_pcrs`                                 | xfailed | xfailed    |
| `tests/test_linux.py::test_legacy_launch_log_declares_the_tpms_banks`                             | xfailed | xfailed    |
| `tests/test_linux.py::test_alt_launch_is_recorded_by_the_platform`                                | xfailed | xfailed    |
| `tests/test_linux.py::test_alt_launch_is_seen_by_linux`                                           | xfailed | xfailed    |
| `tests/test_linux.py::test_alt_launch_log_replays_to_the_pcrs`                                    | xfailed | xfailed    |
| `tests/test_linux.py::test_alt_launch_log_declares_the_tpms_banks`                                | xfailed | xfailed    |
| `tests/test_linux.py::test_the_command_line_is_measured_into_pcr_18_alone`                        | xfailed | xfailed    |
| `tests/test_linux.py::test_normal_boot_launches_nothing`                                          | passed  | passed     |
| `tests/test_matrix.py::test_the_workflow_gets_every_release_under_every_configuration`            | passed  | passed     |
| `tests/test_matrix.py::test_a_selection_of_releases_is_kept_in_the_order_given`                   | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env0-classic]`                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env1-psp]`                    | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env2-sha256]`                 | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env3-psp-sha256]`             | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env4-sha384]`                 | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env5-psp]`                    | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env6-None]`                   | passed  | passed     |
| `tests/test_matrix.py::test_a_cell_replaces_the_configuration_variables_and_the_local_image`      | passed  | passed     |
| `tests/test_menu.py::test_titles_come_out_in_menu_order_once_each`                                | passed  | passed     |
| `tests/test_menu.py::test_the_image_lists_every_entry_this_suite_knows`                           | passed  | passed     |
| `tests/test_qemu_binary.py::test_the_configured_binary_is_ours`                                   | passed  | passed     |
| `tests/test_qemu_binary.py::test_a_refused_option_is_reported`                                    | passed  | passed     |
| `tests/test_qemu_binary.py::test_a_warning_named_in_rejects_is_reported`                          | passed  | passed     |
| `tests/test_qemu_binary.py::test_a_missing_binary_is_reported`                                    | passed  | passed     |
| `tests/test_report.py::test_a_cell_says_what_the_boot_did`                                        | passed  | passed     |
| `tests/test_report.py::test_the_notes_say_what_was_expected`                                      | passed  | passed     |
| `tests/test_report.py::test_a_release_without_results_is_a_missing_column`                        | passed  | passed     |
| `tests/test_report.py::test_the_full_table_has_every_test_and_the_parser_ones_only_there`         | passed  | passed     |
| `tests/test_report.py::test_the_sections_and_columns_follow_the_matrix_order`                     | passed  | passed     |
| `tests/test_report.py::test_the_header_names_the_commit_the_run_and_the_tools`                    | passed  | passed     |
| `tests/test_report.py::test_a_badge_is_green_only_when_every_configuration_passed`                | passed  | passed     |
| `tests/test_report.py::test_a_missing_configuration_alone_is_red_too`                             | passed  | passed     |
| `tests/test_report.py::test_a_hand_made_session_gets_a_section_of_its_own`                        | passed  | passed     |
| `tests/test_report.py::test_main_reads_a_tree_of_results_and_writes_the_page_and_badges`          | passed  | passed     |
| `tests/test_xen.py::test_efi_launch_is_recorded_by_the_platform`                                  | passed  | passed     |
| `tests/test_xen.py::test_efi_launch_is_seen_by_xen`                                               | passed  | passed     |
| `tests/test_xen.py::test_efi_launch_brings_the_iommu_up`                                          | passed  | passed     |
| `tests/test_xen.py::test_efi_launch_log_replays_to_the_pcrs`                                      | passed  | passed     |
| `tests/test_xen.py::test_efi_launch_log_declares_the_tpms_banks`                                  | xfailed | xfailed    |
| `tests/test_xen.py::test_efi_normal_boot_launches_nothing`                                        | passed  | passed     |
| `tests/test_xen.py::test_mb2_launch_is_recorded_by_the_platform`                                  | passed  | passed     |
| `tests/test_xen.py::test_mb2_launch_is_seen_by_xen`                                               | passed  | passed     |
| `tests/test_xen.py::test_mb2_launch_brings_the_iommu_up`                                          | passed  | passed     |
| `tests/test_xen.py::test_mb2_launch_log_replays_to_the_pcrs`                                      | xfailed | xfailed    |
| `tests/test_xen.py::test_mb2_launch_log_declares_the_tpms_banks`                                  | xfailed | xfailed    |

</details>
