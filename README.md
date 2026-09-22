# Boot matrix results

Commit `f0b6ff881b9d`, run [7](https://github.com/iwanicki92/drtm-tests/actions/runs/35785121462), finished 2026-09-22 21:17:37.
QEMU bundle `drtm-11.1.1-1` (11.1.1 (v11.1.1-43-gff57ce2273-dirty)), swtpm 0.7.3.

Rows are the GRUB entries the suite boots, named as their fixtures
in `tests/conftest.py`, columns the releases. ✅ every test of the
entry passed, ❌ one failed, - nothing ran. A mark says what the
boot did, and the notes under the table what the suite expected of it.

## Classic launch, TPM with SHA-1 and SHA-256

| Entry                 | amd-drtm-test-image | v0.5.2 | v0.5.3-rc1 |
|-----------------------|---------------------|--------|------------|
| `xen_efi_launch`      | ✅                   | ✅      | ✅          |
| `xen_efi`             | ✅                   | ✅      | ✅          |
| `xen_mb2_launch`      | ✅                   | ✅      | ✅          |
| `linux_launch`        | ✅                   | ❌      | ❌          |
| `linux_legacy_launch` | ✅                   | ✅      | ✅          |
| `linux_alt_launch`    | ✅                   | ✅      | ✅          |
| `linux`               | ✅                   | ✅      | ✅          |

- `amd-drtm-test-image`: 85 passed.
- `v0.5.2`: 80 passed, 5 xfailed.
    - `linux_launch` expected: panics in check_timer: SKL entered startup_32, GIF never set
- `v0.5.3-rc1`: 80 passed, 5 xfailed.
    - `linux_launch` expected: panics in check_timer: SKL entered startup_32, GIF never set

<details>
<summary>Every test</summary>

| Test                                                                                              | amd-drtm-test-image | v0.5.2  | v0.5.3-rc1 |
|---------------------------------------------------------------------------------------------------|---------------------|---------|------------|
| `tests/test_console.py::test_a_dump_is_the_bytes_it_spells`                                       | passed              | passed  | passed     |
| `tests/test_console.py::test_the_newlines_a_long_dump_wraps_at_are_ignored`                       | passed              | passed  | passed     |
| `tests/test_console.py::test_a_hypervisor_line_spliced_into_a_dump_is_dropped`                    | passed              | passed  | passed     |
| `tests/test_console.py::test_a_hypervisor_line_spliced_into_the_middle_of_a_byte_is_dropped`      | passed              | passed  | passed     |
| `tests/test_console.py::test_a_dump_that_is_not_hex_still_raises`                                 | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_is_the_skls_events_then_xens`                           | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_the_header_declares_the_banks_in_its_order`                         | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[17-sha256]`                         | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[17-sha1]`                           | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[18-sha256]`                         | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[18-sha1]`                           | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_has_the_kernels_tags`                                 | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[17-sha256]` | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[17-sha1]`   | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[18-sha256]` | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[18-sha1]`   | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_the_zero_tail_of_the_log_region_is_not_an_event`                    | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_an_event_without_the_bank_leaves_that_banks_replay_alone`           | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_an_empty_or_foreign_buffer_is_refused`                              | passed              | passed  | passed     |
| `tests/test_grubcfg.py::test_entries_keep_their_commands_in_order_without_the_noise`              | passed              | passed  | passed     |
| `tests/test_grubcfg.py::test_the_parameter_lands_on_the_kernel_line_alone`                        | passed              | passed  | passed     |
| `tests/test_grubcfg.py::test_an_entry_without_a_kernel_line_is_refused`                           | passed              | passed  | passed     |
| `tests/test_grubcfg.py::test_the_boot_partition_is_the_efi_system_partition`                      | passed              | passed  | passed     |
| `tests/test_grubcfg.py::test_a_disk_without_one_is_refused`                                       | passed              | passed  | passed     |
| `tests/test_linux.py::test_launch_is_recorded_by_the_platform`                                    | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_launch_is_seen_by_linux`                                               | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_launch_brings_the_iommu_up`                                            | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_launch_log_replays_to_the_pcrs`                                        | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_launch_log_declares_the_tpms_banks`                                    | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_legacy_launch_is_recorded_by_the_platform`                             | passed              | passed  | passed     |
| `tests/test_linux.py::test_legacy_launch_is_seen_by_linux`                                        | passed              | passed  | passed     |
| `tests/test_linux.py::test_legacy_launch_brings_the_iommu_up`                                     | passed              | passed  | passed     |
| `tests/test_linux.py::test_legacy_launch_log_replays_to_the_pcrs`                                 | passed              | passed  | passed     |
| `tests/test_linux.py::test_legacy_launch_log_declares_the_tpms_banks`                             | passed              | passed  | passed     |
| `tests/test_linux.py::test_alt_launch_is_recorded_by_the_platform`                                | passed              | passed  | passed     |
| `tests/test_linux.py::test_alt_launch_is_seen_by_linux`                                           | passed              | passed  | passed     |
| `tests/test_linux.py::test_alt_launch_log_replays_to_the_pcrs`                                    | passed              | passed  | passed     |
| `tests/test_linux.py::test_alt_launch_log_declares_the_tpms_banks`                                | passed              | passed  | passed     |
| `tests/test_linux.py::test_the_command_line_is_measured_into_pcr_18_alone`                        | passed              | passed  | passed     |
| `tests/test_linux.py::test_normal_boot_launches_nothing`                                          | passed              | passed  | passed     |
| `tests/test_matrix.py::test_the_workflow_gets_every_release_under_every_configuration`            | passed              | passed  | passed     |
| `tests/test_matrix.py::test_a_selection_of_releases_is_kept_in_the_order_given`                   | passed              | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env0-classic]`                | passed              | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env1-psp]`                    | passed              | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env2-sha256]`                 | passed              | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env3-psp-sha256]`             | passed              | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env4-sha384]`                 | passed              | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env5-psp]`                    | passed              | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env6-None]`                   | passed              | passed  | passed     |
| `tests/test_matrix.py::test_a_cell_replaces_the_configuration_variables_and_the_local_image`      | passed              | passed  | passed     |
| `tests/test_menu.py::test_titles_come_out_in_menu_order_once_each`                                | passed              | passed  | passed     |
| `tests/test_menu.py::test_the_image_lists_every_entry_this_suite_knows`                           | passed              | passed  | passed     |
| `tests/test_qemu_binary.py::test_the_configured_binary_is_ours`                                   | passed              | passed  | passed     |
| `tests/test_qemu_binary.py::test_a_refused_option_is_reported`                                    | passed              | passed  | passed     |
| `tests/test_qemu_binary.py::test_a_warning_named_in_rejects_is_reported`                          | passed              | passed  | passed     |
| `tests/test_qemu_binary.py::test_a_missing_binary_is_reported`                                    | passed              | passed  | passed     |
| `tests/test_qemu_vm.py::test_settings_hold_what_the_environment_said_when_read`                   | passed              | passed  | passed     |
| `tests/test_qemu_vm.py::test_settings_name_the_swtpm_programs_by_path`                            | passed              | passed  | passed     |
| `tests/test_qemu_vm.py::test_settings_keep_a_missing_program_by_name`                             | passed              | passed  | passed     |
| `tests/test_qemu_vm.py::test_a_vm_keeps_the_settings_it_was_made_with`                            | passed              | passed  | passed     |
| `tests/test_qemu_vm.py::test_options_end_with_the_extra_arguments_given[extra0-expected0]`        | passed              | passed  | passed     |
| `tests/test_qemu_vm.py::test_options_end_with_the_extra_arguments_given[extra1-expected1]`        | passed              | passed  | passed     |
| `tests/test_qemu_vm.py::test_options_end_with_the_extra_arguments_given[None-expected2]`          | passed              | passed  | passed     |
| `tests/test_qemu_vm.py::test_the_state_is_written_by_the_program_given`                           | passed              | passed  | passed     |
| `tests/test_report.py::test_a_cell_says_what_the_boot_did`                                        | passed              | passed  | passed     |
| `tests/test_report.py::test_the_notes_say_what_was_expected`                                      | passed              | passed  | passed     |
| `tests/test_report.py::test_a_release_without_results_is_a_missing_column`                        | passed              | passed  | passed     |
| `tests/test_report.py::test_the_full_table_has_every_test_and_the_parser_ones_only_there`         | passed              | passed  | passed     |
| `tests/test_report.py::test_the_sections_and_columns_follow_the_matrix_order`                     | passed              | passed  | passed     |
| `tests/test_report.py::test_the_header_names_the_commit_the_run_and_the_tools`                    | passed              | passed  | passed     |
| `tests/test_report.py::test_a_badge_is_green_only_when_every_configuration_passed`                | passed              | passed  | passed     |
| `tests/test_report.py::test_a_missing_configuration_alone_is_red_too`                             | passed              | passed  | passed     |
| `tests/test_report.py::test_a_hand_made_session_gets_a_section_of_its_own`                        | passed              | passed  | passed     |
| `tests/test_report.py::test_main_reads_a_tree_of_results_and_writes_the_page_and_badges`          | passed              | passed  | passed     |
| `tests/test_xen.py::test_efi_launch_is_recorded_by_the_platform`                                  | passed              | passed  | passed     |
| `tests/test_xen.py::test_efi_launch_is_seen_by_xen`                                               | passed              | passed  | passed     |
| `tests/test_xen.py::test_efi_launch_brings_the_iommu_up`                                          | passed              | passed  | passed     |
| `tests/test_xen.py::test_efi_launch_log_replays_to_the_pcrs`                                      | passed              | passed  | passed     |
| `tests/test_xen.py::test_efi_launch_log_declares_the_tpms_banks`                                  | passed              | passed  | passed     |
| `tests/test_xen.py::test_efi_normal_boot_launches_nothing`                                        | passed              | passed  | passed     |
| `tests/test_xen.py::test_mb2_launch_is_recorded_by_the_platform`                                  | passed              | passed  | passed     |
| `tests/test_xen.py::test_mb2_launch_is_seen_by_xen`                                               | passed              | passed  | passed     |
| `tests/test_xen.py::test_mb2_launch_brings_the_iommu_up`                                          | passed              | passed  | passed     |
| `tests/test_xen.py::test_mb2_launch_log_replays_to_the_pcrs`                                      | passed              | passed  | passed     |
| `tests/test_xen.py::test_mb2_launch_log_declares_the_tpms_banks`                                  | passed              | passed  | passed     |

</details>

## PSP DRTM service on

| Entry                 | amd-drtm-test-image | v0.5.2 | v0.5.3-rc1 |
|-----------------------|---------------------|--------|------------|
| `xen_efi_launch`      | ✅                   | ❌      | ❌          |
| `xen_efi`             | ✅                   | ✅      | ✅          |
| `xen_mb2_launch`      | ✅                   | ❌      | ❌          |
| `linux_launch`        | ✅                   | ❌      | ❌          |
| `linux_legacy_launch` | ✅                   | ❌      | ❌          |
| `linux_alt_launch`    | ✅                   | ❌      | ❌          |
| `linux`               | ✅                   | ✅      | ✅          |

- `amd-drtm-test-image`: 85 passed.
- `v0.5.2`: 64 passed, 21 xfailed.
    - `linux_launch` expected: classic SKL: the kernel's extend fails at a locked locality, it panics
    - `linux_legacy_launch` expected: classic SKL: the kernel's extend fails at a locked locality, it panics
    - `linux_alt_launch` expected: classic SKL: the kernel's extend fails at a locked locality, it panics
    - `xen_efi_launch` expected: classic SKL: no LAUNCH, so the PSP's locality locks stay on the TPM
    - `xen_mb2_launch` expected: classic SKL: no LAUNCH, so the PSP's locality locks stay on the TPM
- `v0.5.3-rc1`: 64 passed, 21 xfailed.
    - `linux_launch` expected: classic SKL: the kernel's extend fails at a locked locality, it panics
    - `linux_legacy_launch` expected: classic SKL: the kernel's extend fails at a locked locality, it panics
    - `linux_alt_launch` expected: classic SKL: the kernel's extend fails at a locked locality, it panics
    - `xen_efi_launch` expected: classic SKL: no LAUNCH, so the PSP's locality locks stay on the TPM
    - `xen_mb2_launch` expected: classic SKL: no LAUNCH, so the PSP's locality locks stay on the TPM

<details>
<summary>Every test</summary>

| Test                                                                                              | amd-drtm-test-image | v0.5.2  | v0.5.3-rc1 |
|---------------------------------------------------------------------------------------------------|---------------------|---------|------------|
| `tests/test_console.py::test_a_dump_is_the_bytes_it_spells`                                       | passed              | passed  | passed     |
| `tests/test_console.py::test_the_newlines_a_long_dump_wraps_at_are_ignored`                       | passed              | passed  | passed     |
| `tests/test_console.py::test_a_hypervisor_line_spliced_into_a_dump_is_dropped`                    | passed              | passed  | passed     |
| `tests/test_console.py::test_a_hypervisor_line_spliced_into_the_middle_of_a_byte_is_dropped`      | passed              | passed  | passed     |
| `tests/test_console.py::test_a_dump_that_is_not_hex_still_raises`                                 | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_is_the_skls_events_then_xens`                           | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_the_header_declares_the_banks_in_its_order`                         | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[17-sha256]`                         | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[17-sha1]`                           | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[18-sha256]`                         | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[18-sha1]`                           | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_has_the_kernels_tags`                                 | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[17-sha256]` | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[17-sha1]`   | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[18-sha256]` | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[18-sha1]`   | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_the_zero_tail_of_the_log_region_is_not_an_event`                    | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_an_event_without_the_bank_leaves_that_banks_replay_alone`           | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_an_empty_or_foreign_buffer_is_refused`                              | passed              | passed  | passed     |
| `tests/test_grubcfg.py::test_entries_keep_their_commands_in_order_without_the_noise`              | passed              | passed  | passed     |
| `tests/test_grubcfg.py::test_the_parameter_lands_on_the_kernel_line_alone`                        | passed              | passed  | passed     |
| `tests/test_grubcfg.py::test_an_entry_without_a_kernel_line_is_refused`                           | passed              | passed  | passed     |
| `tests/test_grubcfg.py::test_the_boot_partition_is_the_efi_system_partition`                      | passed              | passed  | passed     |
| `tests/test_grubcfg.py::test_a_disk_without_one_is_refused`                                       | passed              | passed  | passed     |
| `tests/test_linux.py::test_launch_is_recorded_by_the_platform`                                    | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_launch_is_seen_by_linux`                                               | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_launch_brings_the_iommu_up`                                            | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_launch_log_replays_to_the_pcrs`                                        | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_launch_log_declares_the_tpms_banks`                                    | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_legacy_launch_is_recorded_by_the_platform`                             | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_legacy_launch_is_seen_by_linux`                                        | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_legacy_launch_brings_the_iommu_up`                                     | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_legacy_launch_log_replays_to_the_pcrs`                                 | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_legacy_launch_log_declares_the_tpms_banks`                             | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_alt_launch_is_recorded_by_the_platform`                                | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_alt_launch_is_seen_by_linux`                                           | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_alt_launch_log_replays_to_the_pcrs`                                    | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_alt_launch_log_declares_the_tpms_banks`                                | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_the_command_line_is_measured_into_pcr_18_alone`                        | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_normal_boot_launches_nothing`                                          | passed              | passed  | passed     |
| `tests/test_matrix.py::test_the_workflow_gets_every_release_under_every_configuration`            | passed              | passed  | passed     |
| `tests/test_matrix.py::test_a_selection_of_releases_is_kept_in_the_order_given`                   | passed              | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env0-classic]`                | passed              | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env1-psp]`                    | passed              | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env2-sha256]`                 | passed              | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env3-psp-sha256]`             | passed              | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env4-sha384]`                 | passed              | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env5-psp]`                    | passed              | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env6-None]`                   | passed              | passed  | passed     |
| `tests/test_matrix.py::test_a_cell_replaces_the_configuration_variables_and_the_local_image`      | passed              | passed  | passed     |
| `tests/test_menu.py::test_titles_come_out_in_menu_order_once_each`                                | passed              | passed  | passed     |
| `tests/test_menu.py::test_the_image_lists_every_entry_this_suite_knows`                           | passed              | passed  | passed     |
| `tests/test_qemu_binary.py::test_the_configured_binary_is_ours`                                   | passed              | passed  | passed     |
| `tests/test_qemu_binary.py::test_a_refused_option_is_reported`                                    | passed              | passed  | passed     |
| `tests/test_qemu_binary.py::test_a_warning_named_in_rejects_is_reported`                          | passed              | passed  | passed     |
| `tests/test_qemu_binary.py::test_a_missing_binary_is_reported`                                    | passed              | passed  | passed     |
| `tests/test_qemu_vm.py::test_settings_hold_what_the_environment_said_when_read`                   | passed              | passed  | passed     |
| `tests/test_qemu_vm.py::test_settings_name_the_swtpm_programs_by_path`                            | passed              | passed  | passed     |
| `tests/test_qemu_vm.py::test_settings_keep_a_missing_program_by_name`                             | passed              | passed  | passed     |
| `tests/test_qemu_vm.py::test_a_vm_keeps_the_settings_it_was_made_with`                            | passed              | passed  | passed     |
| `tests/test_qemu_vm.py::test_options_end_with_the_extra_arguments_given[extra0-expected0]`        | passed              | passed  | passed     |
| `tests/test_qemu_vm.py::test_options_end_with_the_extra_arguments_given[extra1-expected1]`        | passed              | passed  | passed     |
| `tests/test_qemu_vm.py::test_options_end_with_the_extra_arguments_given[None-expected2]`          | passed              | passed  | passed     |
| `tests/test_qemu_vm.py::test_the_state_is_written_by_the_program_given`                           | passed              | passed  | passed     |
| `tests/test_report.py::test_a_cell_says_what_the_boot_did`                                        | passed              | passed  | passed     |
| `tests/test_report.py::test_the_notes_say_what_was_expected`                                      | passed              | passed  | passed     |
| `tests/test_report.py::test_a_release_without_results_is_a_missing_column`                        | passed              | passed  | passed     |
| `tests/test_report.py::test_the_full_table_has_every_test_and_the_parser_ones_only_there`         | passed              | passed  | passed     |
| `tests/test_report.py::test_the_sections_and_columns_follow_the_matrix_order`                     | passed              | passed  | passed     |
| `tests/test_report.py::test_the_header_names_the_commit_the_run_and_the_tools`                    | passed              | passed  | passed     |
| `tests/test_report.py::test_a_badge_is_green_only_when_every_configuration_passed`                | passed              | passed  | passed     |
| `tests/test_report.py::test_a_missing_configuration_alone_is_red_too`                             | passed              | passed  | passed     |
| `tests/test_report.py::test_a_hand_made_session_gets_a_section_of_its_own`                        | passed              | passed  | passed     |
| `tests/test_report.py::test_main_reads_a_tree_of_results_and_writes_the_page_and_badges`          | passed              | passed  | passed     |
| `tests/test_xen.py::test_efi_launch_is_recorded_by_the_platform`                                  | passed              | xfailed | xfailed    |
| `tests/test_xen.py::test_efi_launch_is_seen_by_xen`                                               | passed              | xfailed | xfailed    |
| `tests/test_xen.py::test_efi_launch_brings_the_iommu_up`                                          | passed              | passed  | passed     |
| `tests/test_xen.py::test_efi_launch_log_replays_to_the_pcrs`                                      | passed              | xfailed | xfailed    |
| `tests/test_xen.py::test_efi_launch_log_declares_the_tpms_banks`                                  | passed              | passed  | passed     |
| `tests/test_xen.py::test_efi_normal_boot_launches_nothing`                                        | passed              | passed  | passed     |
| `tests/test_xen.py::test_mb2_launch_is_recorded_by_the_platform`                                  | passed              | xfailed | xfailed    |
| `tests/test_xen.py::test_mb2_launch_is_seen_by_xen`                                               | passed              | xfailed | xfailed    |
| `tests/test_xen.py::test_mb2_launch_brings_the_iommu_up`                                          | passed              | passed  | passed     |
| `tests/test_xen.py::test_mb2_launch_log_replays_to_the_pcrs`                                      | passed              | xfailed | xfailed    |
| `tests/test_xen.py::test_mb2_launch_log_declares_the_tpms_banks`                                  | passed              | passed  | passed     |

</details>

## TPM with SHA-256 alone

| Entry                 | amd-drtm-test-image | v0.5.2 | v0.5.3-rc1 |
|-----------------------|---------------------|--------|------------|
| `xen_efi_launch`      | ✅                   | ❌      | ❌          |
| `xen_efi`             | ✅                   | ✅      | ✅          |
| `xen_mb2_launch`      | ✅                   | ❌      | ❌          |
| `linux_launch`        | ✅                   | ❌      | ❌          |
| `linux_legacy_launch` | ✅                   | ❌      | ❌          |
| `linux_alt_launch`    | ✅                   | ❌      | ❌          |
| `linux`               | ✅                   | ✅      | ✅          |

- `amd-drtm-test-image`: 85 passed.
- `v0.5.2`: 68 passed, 17 xfailed.
    - `linux_launch` expected: panics in check_timer: SKL entered startup_32, GIF never set
    - `linux_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has
    - `linux_legacy_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has
    - `linux_alt_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has
    - `xen_efi_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has
    - `xen_mb2_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has
- `v0.5.3-rc1`: 68 passed, 17 xfailed.
    - `linux_launch` expected: panics in check_timer: SKL entered startup_32, GIF never set
    - `linux_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has
    - `linux_legacy_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has
    - `linux_alt_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has
    - `xen_efi_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has
    - `xen_mb2_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has

<details>
<summary>Every test</summary>

| Test                                                                                              | amd-drtm-test-image | v0.5.2  | v0.5.3-rc1 |
|---------------------------------------------------------------------------------------------------|---------------------|---------|------------|
| `tests/test_console.py::test_a_dump_is_the_bytes_it_spells`                                       | passed              | passed  | passed     |
| `tests/test_console.py::test_the_newlines_a_long_dump_wraps_at_are_ignored`                       | passed              | passed  | passed     |
| `tests/test_console.py::test_a_hypervisor_line_spliced_into_a_dump_is_dropped`                    | passed              | passed  | passed     |
| `tests/test_console.py::test_a_hypervisor_line_spliced_into_the_middle_of_a_byte_is_dropped`      | passed              | passed  | passed     |
| `tests/test_console.py::test_a_dump_that_is_not_hex_still_raises`                                 | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_is_the_skls_events_then_xens`                           | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_the_header_declares_the_banks_in_its_order`                         | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[17-sha256]`                         | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[17-sha1]`                           | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[18-sha256]`                         | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[18-sha1]`                           | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_has_the_kernels_tags`                                 | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[17-sha256]` | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[17-sha1]`   | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[18-sha256]` | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[18-sha1]`   | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_the_zero_tail_of_the_log_region_is_not_an_event`                    | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_an_event_without_the_bank_leaves_that_banks_replay_alone`           | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_an_empty_or_foreign_buffer_is_refused`                              | passed              | passed  | passed     |
| `tests/test_grubcfg.py::test_entries_keep_their_commands_in_order_without_the_noise`              | passed              | passed  | passed     |
| `tests/test_grubcfg.py::test_the_parameter_lands_on_the_kernel_line_alone`                        | passed              | passed  | passed     |
| `tests/test_grubcfg.py::test_an_entry_without_a_kernel_line_is_refused`                           | passed              | passed  | passed     |
| `tests/test_grubcfg.py::test_the_boot_partition_is_the_efi_system_partition`                      | passed              | passed  | passed     |
| `tests/test_grubcfg.py::test_a_disk_without_one_is_refused`                                       | passed              | passed  | passed     |
| `tests/test_linux.py::test_launch_is_recorded_by_the_platform`                                    | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_launch_is_seen_by_linux`                                               | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_launch_brings_the_iommu_up`                                            | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_launch_log_replays_to_the_pcrs`                                        | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_launch_log_declares_the_tpms_banks`                                    | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_legacy_launch_is_recorded_by_the_platform`                             | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_legacy_launch_is_seen_by_linux`                                        | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_legacy_launch_brings_the_iommu_up`                                     | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_legacy_launch_log_replays_to_the_pcrs`                                 | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_legacy_launch_log_declares_the_tpms_banks`                             | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_alt_launch_is_recorded_by_the_platform`                                | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_alt_launch_is_seen_by_linux`                                           | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_alt_launch_log_replays_to_the_pcrs`                                    | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_alt_launch_log_declares_the_tpms_banks`                                | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_the_command_line_is_measured_into_pcr_18_alone`                        | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_normal_boot_launches_nothing`                                          | passed              | passed  | passed     |
| `tests/test_matrix.py::test_the_workflow_gets_every_release_under_every_configuration`            | passed              | passed  | passed     |
| `tests/test_matrix.py::test_a_selection_of_releases_is_kept_in_the_order_given`                   | passed              | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env0-classic]`                | passed              | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env1-psp]`                    | passed              | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env2-sha256]`                 | passed              | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env3-psp-sha256]`             | passed              | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env4-sha384]`                 | passed              | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env5-psp]`                    | passed              | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env6-None]`                   | passed              | passed  | passed     |
| `tests/test_matrix.py::test_a_cell_replaces_the_configuration_variables_and_the_local_image`      | passed              | passed  | passed     |
| `tests/test_menu.py::test_titles_come_out_in_menu_order_once_each`                                | passed              | passed  | passed     |
| `tests/test_menu.py::test_the_image_lists_every_entry_this_suite_knows`                           | passed              | passed  | passed     |
| `tests/test_qemu_binary.py::test_the_configured_binary_is_ours`                                   | passed              | passed  | passed     |
| `tests/test_qemu_binary.py::test_a_refused_option_is_reported`                                    | passed              | passed  | passed     |
| `tests/test_qemu_binary.py::test_a_warning_named_in_rejects_is_reported`                          | passed              | passed  | passed     |
| `tests/test_qemu_binary.py::test_a_missing_binary_is_reported`                                    | passed              | passed  | passed     |
| `tests/test_qemu_vm.py::test_settings_hold_what_the_environment_said_when_read`                   | passed              | passed  | passed     |
| `tests/test_qemu_vm.py::test_settings_name_the_swtpm_programs_by_path`                            | passed              | passed  | passed     |
| `tests/test_qemu_vm.py::test_settings_keep_a_missing_program_by_name`                             | passed              | passed  | passed     |
| `tests/test_qemu_vm.py::test_a_vm_keeps_the_settings_it_was_made_with`                            | passed              | passed  | passed     |
| `tests/test_qemu_vm.py::test_options_end_with_the_extra_arguments_given[extra0-expected0]`        | passed              | passed  | passed     |
| `tests/test_qemu_vm.py::test_options_end_with_the_extra_arguments_given[extra1-expected1]`        | passed              | passed  | passed     |
| `tests/test_qemu_vm.py::test_options_end_with_the_extra_arguments_given[None-expected2]`          | passed              | passed  | passed     |
| `tests/test_qemu_vm.py::test_the_state_is_written_by_the_program_given`                           | passed              | passed  | passed     |
| `tests/test_report.py::test_a_cell_says_what_the_boot_did`                                        | passed              | passed  | passed     |
| `tests/test_report.py::test_the_notes_say_what_was_expected`                                      | passed              | passed  | passed     |
| `tests/test_report.py::test_a_release_without_results_is_a_missing_column`                        | passed              | passed  | passed     |
| `tests/test_report.py::test_the_full_table_has_every_test_and_the_parser_ones_only_there`         | passed              | passed  | passed     |
| `tests/test_report.py::test_the_sections_and_columns_follow_the_matrix_order`                     | passed              | passed  | passed     |
| `tests/test_report.py::test_the_header_names_the_commit_the_run_and_the_tools`                    | passed              | passed  | passed     |
| `tests/test_report.py::test_a_badge_is_green_only_when_every_configuration_passed`                | passed              | passed  | passed     |
| `tests/test_report.py::test_a_missing_configuration_alone_is_red_too`                             | passed              | passed  | passed     |
| `tests/test_report.py::test_a_hand_made_session_gets_a_section_of_its_own`                        | passed              | passed  | passed     |
| `tests/test_report.py::test_main_reads_a_tree_of_results_and_writes_the_page_and_badges`          | passed              | passed  | passed     |
| `tests/test_xen.py::test_efi_launch_is_recorded_by_the_platform`                                  | passed              | passed  | passed     |
| `tests/test_xen.py::test_efi_launch_is_seen_by_xen`                                               | passed              | passed  | passed     |
| `tests/test_xen.py::test_efi_launch_brings_the_iommu_up`                                          | passed              | passed  | passed     |
| `tests/test_xen.py::test_efi_launch_log_replays_to_the_pcrs`                                      | passed              | passed  | passed     |
| `tests/test_xen.py::test_efi_launch_log_declares_the_tpms_banks`                                  | passed              | xfailed | xfailed    |
| `tests/test_xen.py::test_efi_normal_boot_launches_nothing`                                        | passed              | passed  | passed     |
| `tests/test_xen.py::test_mb2_launch_is_recorded_by_the_platform`                                  | passed              | passed  | passed     |
| `tests/test_xen.py::test_mb2_launch_is_seen_by_xen`                                               | passed              | passed  | passed     |
| `tests/test_xen.py::test_mb2_launch_brings_the_iommu_up`                                          | passed              | passed  | passed     |
| `tests/test_xen.py::test_mb2_launch_log_replays_to_the_pcrs`                                      | passed              | passed  | passed     |
| `tests/test_xen.py::test_mb2_launch_log_declares_the_tpms_banks`                                  | passed              | xfailed | xfailed    |

</details>

## PSP DRTM service on, SHA-256 alone

| Entry                 | amd-drtm-test-image | v0.5.2 | v0.5.3-rc1 |
|-----------------------|---------------------|--------|------------|
| `xen_efi_launch`      | ✅                   | ❌      | ❌          |
| `xen_efi`             | ✅                   | ✅      | ✅          |
| `xen_mb2_launch`      | ✅                   | ❌      | ❌          |
| `linux_launch`        | ✅                   | ❌      | ❌          |
| `linux_legacy_launch` | ✅                   | ❌      | ❌          |
| `linux_alt_launch`    | ✅                   | ❌      | ❌          |
| `linux`               | ✅                   | ✅      | ✅          |

- `amd-drtm-test-image`: 85 passed.
- `v0.5.2`: 62 passed, 23 xfailed.
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
- `v0.5.3-rc1`: 62 passed, 23 xfailed.
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

<details>
<summary>Every test</summary>

| Test                                                                                              | amd-drtm-test-image | v0.5.2  | v0.5.3-rc1 |
|---------------------------------------------------------------------------------------------------|---------------------|---------|------------|
| `tests/test_console.py::test_a_dump_is_the_bytes_it_spells`                                       | passed              | passed  | passed     |
| `tests/test_console.py::test_the_newlines_a_long_dump_wraps_at_are_ignored`                       | passed              | passed  | passed     |
| `tests/test_console.py::test_a_hypervisor_line_spliced_into_a_dump_is_dropped`                    | passed              | passed  | passed     |
| `tests/test_console.py::test_a_hypervisor_line_spliced_into_the_middle_of_a_byte_is_dropped`      | passed              | passed  | passed     |
| `tests/test_console.py::test_a_dump_that_is_not_hex_still_raises`                                 | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_is_the_skls_events_then_xens`                           | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_the_header_declares_the_banks_in_its_order`                         | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[17-sha256]`                         | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[17-sha1]`                           | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[18-sha256]`                         | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[18-sha1]`                           | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_has_the_kernels_tags`                                 | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[17-sha256]` | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[17-sha1]`   | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[18-sha256]` | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[18-sha1]`   | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_the_zero_tail_of_the_log_region_is_not_an_event`                    | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_an_event_without_the_bank_leaves_that_banks_replay_alone`           | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_an_empty_or_foreign_buffer_is_refused`                              | passed              | passed  | passed     |
| `tests/test_grubcfg.py::test_entries_keep_their_commands_in_order_without_the_noise`              | passed              | passed  | passed     |
| `tests/test_grubcfg.py::test_the_parameter_lands_on_the_kernel_line_alone`                        | passed              | passed  | passed     |
| `tests/test_grubcfg.py::test_an_entry_without_a_kernel_line_is_refused`                           | passed              | passed  | passed     |
| `tests/test_grubcfg.py::test_the_boot_partition_is_the_efi_system_partition`                      | passed              | passed  | passed     |
| `tests/test_grubcfg.py::test_a_disk_without_one_is_refused`                                       | passed              | passed  | passed     |
| `tests/test_linux.py::test_launch_is_recorded_by_the_platform`                                    | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_launch_is_seen_by_linux`                                               | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_launch_brings_the_iommu_up`                                            | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_launch_log_replays_to_the_pcrs`                                        | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_launch_log_declares_the_tpms_banks`                                    | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_legacy_launch_is_recorded_by_the_platform`                             | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_legacy_launch_is_seen_by_linux`                                        | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_legacy_launch_brings_the_iommu_up`                                     | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_legacy_launch_log_replays_to_the_pcrs`                                 | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_legacy_launch_log_declares_the_tpms_banks`                             | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_alt_launch_is_recorded_by_the_platform`                                | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_alt_launch_is_seen_by_linux`                                           | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_alt_launch_log_replays_to_the_pcrs`                                    | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_alt_launch_log_declares_the_tpms_banks`                                | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_the_command_line_is_measured_into_pcr_18_alone`                        | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_normal_boot_launches_nothing`                                          | passed              | passed  | passed     |
| `tests/test_matrix.py::test_the_workflow_gets_every_release_under_every_configuration`            | passed              | passed  | passed     |
| `tests/test_matrix.py::test_a_selection_of_releases_is_kept_in_the_order_given`                   | passed              | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env0-classic]`                | passed              | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env1-psp]`                    | passed              | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env2-sha256]`                 | passed              | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env3-psp-sha256]`             | passed              | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env4-sha384]`                 | passed              | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env5-psp]`                    | passed              | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env6-None]`                   | passed              | passed  | passed     |
| `tests/test_matrix.py::test_a_cell_replaces_the_configuration_variables_and_the_local_image`      | passed              | passed  | passed     |
| `tests/test_menu.py::test_titles_come_out_in_menu_order_once_each`                                | passed              | passed  | passed     |
| `tests/test_menu.py::test_the_image_lists_every_entry_this_suite_knows`                           | passed              | passed  | passed     |
| `tests/test_qemu_binary.py::test_the_configured_binary_is_ours`                                   | passed              | passed  | passed     |
| `tests/test_qemu_binary.py::test_a_refused_option_is_reported`                                    | passed              | passed  | passed     |
| `tests/test_qemu_binary.py::test_a_warning_named_in_rejects_is_reported`                          | passed              | passed  | passed     |
| `tests/test_qemu_binary.py::test_a_missing_binary_is_reported`                                    | passed              | passed  | passed     |
| `tests/test_qemu_vm.py::test_settings_hold_what_the_environment_said_when_read`                   | passed              | passed  | passed     |
| `tests/test_qemu_vm.py::test_settings_name_the_swtpm_programs_by_path`                            | passed              | passed  | passed     |
| `tests/test_qemu_vm.py::test_settings_keep_a_missing_program_by_name`                             | passed              | passed  | passed     |
| `tests/test_qemu_vm.py::test_a_vm_keeps_the_settings_it_was_made_with`                            | passed              | passed  | passed     |
| `tests/test_qemu_vm.py::test_options_end_with_the_extra_arguments_given[extra0-expected0]`        | passed              | passed  | passed     |
| `tests/test_qemu_vm.py::test_options_end_with_the_extra_arguments_given[extra1-expected1]`        | passed              | passed  | passed     |
| `tests/test_qemu_vm.py::test_options_end_with_the_extra_arguments_given[None-expected2]`          | passed              | passed  | passed     |
| `tests/test_qemu_vm.py::test_the_state_is_written_by_the_program_given`                           | passed              | passed  | passed     |
| `tests/test_report.py::test_a_cell_says_what_the_boot_did`                                        | passed              | passed  | passed     |
| `tests/test_report.py::test_the_notes_say_what_was_expected`                                      | passed              | passed  | passed     |
| `tests/test_report.py::test_a_release_without_results_is_a_missing_column`                        | passed              | passed  | passed     |
| `tests/test_report.py::test_the_full_table_has_every_test_and_the_parser_ones_only_there`         | passed              | passed  | passed     |
| `tests/test_report.py::test_the_sections_and_columns_follow_the_matrix_order`                     | passed              | passed  | passed     |
| `tests/test_report.py::test_the_header_names_the_commit_the_run_and_the_tools`                    | passed              | passed  | passed     |
| `tests/test_report.py::test_a_badge_is_green_only_when_every_configuration_passed`                | passed              | passed  | passed     |
| `tests/test_report.py::test_a_missing_configuration_alone_is_red_too`                             | passed              | passed  | passed     |
| `tests/test_report.py::test_a_hand_made_session_gets_a_section_of_its_own`                        | passed              | passed  | passed     |
| `tests/test_report.py::test_main_reads_a_tree_of_results_and_writes_the_page_and_badges`          | passed              | passed  | passed     |
| `tests/test_xen.py::test_efi_launch_is_recorded_by_the_platform`                                  | passed              | xfailed | xfailed    |
| `tests/test_xen.py::test_efi_launch_is_seen_by_xen`                                               | passed              | xfailed | xfailed    |
| `tests/test_xen.py::test_efi_launch_brings_the_iommu_up`                                          | passed              | passed  | passed     |
| `tests/test_xen.py::test_efi_launch_log_replays_to_the_pcrs`                                      | passed              | xfailed | xfailed    |
| `tests/test_xen.py::test_efi_launch_log_declares_the_tpms_banks`                                  | passed              | xfailed | xfailed    |
| `tests/test_xen.py::test_efi_normal_boot_launches_nothing`                                        | passed              | passed  | passed     |
| `tests/test_xen.py::test_mb2_launch_is_recorded_by_the_platform`                                  | passed              | xfailed | xfailed    |
| `tests/test_xen.py::test_mb2_launch_is_seen_by_xen`                                               | passed              | xfailed | xfailed    |
| `tests/test_xen.py::test_mb2_launch_brings_the_iommu_up`                                          | passed              | passed  | passed     |
| `tests/test_xen.py::test_mb2_launch_log_replays_to_the_pcrs`                                      | passed              | xfailed | xfailed    |
| `tests/test_xen.py::test_mb2_launch_log_declares_the_tpms_banks`                                  | passed              | xfailed | xfailed    |

</details>

## TPM with SHA-384 on top

| Entry                 | amd-drtm-test-image | v0.5.2 | v0.5.3-rc1 |
|-----------------------|---------------------|--------|------------|
| `xen_efi_launch`      | ✅                   | ❌      | ❌          |
| `xen_efi`             | ✅                   | ✅      | ❌          |
| `xen_mb2_launch`      | ✅                   | ❌      | ❌          |
| `linux_launch`        | ✅                   | ❌      | ❌          |
| `linux_legacy_launch` | ✅                   | ❌      | ❌          |
| `linux_alt_launch`    | ✅                   | ❌      | ❌          |
| `linux`               | ✅                   | ✅      | ✅          |

- `amd-drtm-test-image`: 85 passed.
- `v0.5.2`: 67 passed, 18 xfailed.
    - `linux_launch` expected: panics in check_timer: SKL entered startup_32, GIF never set
    - `linux_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has
    - `linux_legacy_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has
    - `linux_alt_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has
    - `xen_efi_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has
    - `xen_mb2_launch` expected: the upstream Xen copies the MBI's digests for SHA-1 and SHA-256 alone
    - `xen_mb2_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has
- `v0.5.3-rc1`: 2 failed, 65 passed, 18 xfailed.
    - `linux_launch` expected: panics in check_timer: SKL entered startup_32, GIF never set
    - `linux_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has
    - `linux_legacy_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has
    - `linux_alt_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has
    - `xen_efi`: 2 failed unexpectedly
    - `xen_efi_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has
    - `xen_mb2_launch` expected: the upstream Xen copies the MBI's digests for SHA-1 and SHA-256 alone
    - `xen_mb2_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has

<details>
<summary>Every test</summary>

| Test                                                                                              | amd-drtm-test-image | v0.5.2  | v0.5.3-rc1 |
|---------------------------------------------------------------------------------------------------|---------------------|---------|------------|
| `tests/test_console.py::test_a_dump_is_the_bytes_it_spells`                                       | passed              | passed  | passed     |
| `tests/test_console.py::test_the_newlines_a_long_dump_wraps_at_are_ignored`                       | passed              | passed  | passed     |
| `tests/test_console.py::test_a_hypervisor_line_spliced_into_a_dump_is_dropped`                    | passed              | passed  | passed     |
| `tests/test_console.py::test_a_hypervisor_line_spliced_into_the_middle_of_a_byte_is_dropped`      | passed              | passed  | passed     |
| `tests/test_console.py::test_a_dump_that_is_not_hex_still_raises`                                 | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_is_the_skls_events_then_xens`                           | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_the_header_declares_the_banks_in_its_order`                         | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[17-sha256]`                         | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[17-sha1]`                           | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[18-sha256]`                         | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[18-sha1]`                           | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_has_the_kernels_tags`                                 | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[17-sha256]` | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[17-sha1]`   | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[18-sha256]` | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[18-sha1]`   | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_the_zero_tail_of_the_log_region_is_not_an_event`                    | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_an_event_without_the_bank_leaves_that_banks_replay_alone`           | passed              | passed  | passed     |
| `tests/test_eventlog.py::test_an_empty_or_foreign_buffer_is_refused`                              | passed              | passed  | passed     |
| `tests/test_grubcfg.py::test_entries_keep_their_commands_in_order_without_the_noise`              | passed              | passed  | passed     |
| `tests/test_grubcfg.py::test_the_parameter_lands_on_the_kernel_line_alone`                        | passed              | passed  | passed     |
| `tests/test_grubcfg.py::test_an_entry_without_a_kernel_line_is_refused`                           | passed              | passed  | passed     |
| `tests/test_grubcfg.py::test_the_boot_partition_is_the_efi_system_partition`                      | passed              | passed  | passed     |
| `tests/test_grubcfg.py::test_a_disk_without_one_is_refused`                                       | passed              | passed  | passed     |
| `tests/test_linux.py::test_launch_is_recorded_by_the_platform`                                    | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_launch_is_seen_by_linux`                                               | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_launch_brings_the_iommu_up`                                            | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_launch_log_replays_to_the_pcrs`                                        | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_launch_log_declares_the_tpms_banks`                                    | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_legacy_launch_is_recorded_by_the_platform`                             | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_legacy_launch_is_seen_by_linux`                                        | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_legacy_launch_brings_the_iommu_up`                                     | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_legacy_launch_log_replays_to_the_pcrs`                                 | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_legacy_launch_log_declares_the_tpms_banks`                             | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_alt_launch_is_recorded_by_the_platform`                                | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_alt_launch_is_seen_by_linux`                                           | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_alt_launch_log_replays_to_the_pcrs`                                    | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_alt_launch_log_declares_the_tpms_banks`                                | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_the_command_line_is_measured_into_pcr_18_alone`                        | passed              | xfailed | xfailed    |
| `tests/test_linux.py::test_normal_boot_launches_nothing`                                          | passed              | passed  | passed     |
| `tests/test_matrix.py::test_the_workflow_gets_every_release_under_every_configuration`            | passed              | passed  | passed     |
| `tests/test_matrix.py::test_a_selection_of_releases_is_kept_in_the_order_given`                   | passed              | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env0-classic]`                | passed              | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env1-psp]`                    | passed              | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env2-sha256]`                 | passed              | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env3-psp-sha256]`             | passed              | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env4-sha384]`                 | passed              | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env5-psp]`                    | passed              | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env6-None]`                   | passed              | passed  | passed     |
| `tests/test_matrix.py::test_a_cell_replaces_the_configuration_variables_and_the_local_image`      | passed              | passed  | passed     |
| `tests/test_menu.py::test_titles_come_out_in_menu_order_once_each`                                | passed              | passed  | passed     |
| `tests/test_menu.py::test_the_image_lists_every_entry_this_suite_knows`                           | passed              | passed  | failed     |
| `tests/test_qemu_binary.py::test_the_configured_binary_is_ours`                                   | passed              | passed  | passed     |
| `tests/test_qemu_binary.py::test_a_refused_option_is_reported`                                    | passed              | passed  | passed     |
| `tests/test_qemu_binary.py::test_a_warning_named_in_rejects_is_reported`                          | passed              | passed  | passed     |
| `tests/test_qemu_binary.py::test_a_missing_binary_is_reported`                                    | passed              | passed  | passed     |
| `tests/test_qemu_vm.py::test_settings_hold_what_the_environment_said_when_read`                   | passed              | passed  | passed     |
| `tests/test_qemu_vm.py::test_settings_name_the_swtpm_programs_by_path`                            | passed              | passed  | passed     |
| `tests/test_qemu_vm.py::test_settings_keep_a_missing_program_by_name`                             | passed              | passed  | passed     |
| `tests/test_qemu_vm.py::test_a_vm_keeps_the_settings_it_was_made_with`                            | passed              | passed  | passed     |
| `tests/test_qemu_vm.py::test_options_end_with_the_extra_arguments_given[extra0-expected0]`        | passed              | passed  | passed     |
| `tests/test_qemu_vm.py::test_options_end_with_the_extra_arguments_given[extra1-expected1]`        | passed              | passed  | passed     |
| `tests/test_qemu_vm.py::test_options_end_with_the_extra_arguments_given[None-expected2]`          | passed              | passed  | passed     |
| `tests/test_qemu_vm.py::test_the_state_is_written_by_the_program_given`                           | passed              | passed  | passed     |
| `tests/test_report.py::test_a_cell_says_what_the_boot_did`                                        | passed              | passed  | passed     |
| `tests/test_report.py::test_the_notes_say_what_was_expected`                                      | passed              | passed  | passed     |
| `tests/test_report.py::test_a_release_without_results_is_a_missing_column`                        | passed              | passed  | passed     |
| `tests/test_report.py::test_the_full_table_has_every_test_and_the_parser_ones_only_there`         | passed              | passed  | passed     |
| `tests/test_report.py::test_the_sections_and_columns_follow_the_matrix_order`                     | passed              | passed  | passed     |
| `tests/test_report.py::test_the_header_names_the_commit_the_run_and_the_tools`                    | passed              | passed  | passed     |
| `tests/test_report.py::test_a_badge_is_green_only_when_every_configuration_passed`                | passed              | passed  | passed     |
| `tests/test_report.py::test_a_missing_configuration_alone_is_red_too`                             | passed              | passed  | passed     |
| `tests/test_report.py::test_a_hand_made_session_gets_a_section_of_its_own`                        | passed              | passed  | passed     |
| `tests/test_report.py::test_main_reads_a_tree_of_results_and_writes_the_page_and_badges`          | passed              | passed  | passed     |
| `tests/test_xen.py::test_efi_launch_is_recorded_by_the_platform`                                  | passed              | passed  | passed     |
| `tests/test_xen.py::test_efi_launch_is_seen_by_xen`                                               | passed              | passed  | passed     |
| `tests/test_xen.py::test_efi_launch_brings_the_iommu_up`                                          | passed              | passed  | passed     |
| `tests/test_xen.py::test_efi_launch_log_replays_to_the_pcrs`                                      | passed              | passed  | passed     |
| `tests/test_xen.py::test_efi_launch_log_declares_the_tpms_banks`                                  | passed              | xfailed | xfailed    |
| `tests/test_xen.py::test_efi_normal_boot_launches_nothing`                                        | passed              | passed  | failed     |
| `tests/test_xen.py::test_mb2_launch_is_recorded_by_the_platform`                                  | passed              | passed  | passed     |
| `tests/test_xen.py::test_mb2_launch_is_seen_by_xen`                                               | passed              | passed  | passed     |
| `tests/test_xen.py::test_mb2_launch_brings_the_iommu_up`                                          | passed              | passed  | passed     |
| `tests/test_xen.py::test_mb2_launch_log_replays_to_the_pcrs`                                      | passed              | xfailed | xfailed    |
| `tests/test_xen.py::test_mb2_launch_log_declares_the_tpms_banks`                                  | passed              | xfailed | xfailed    |

</details>
