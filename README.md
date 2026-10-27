# Boot matrix results

Commit `f88f3ee57e99`, run [13](https://github.com/iwanicki92/drtm-tests/actions/runs/40601570445), finished 2026-10-27 23:32:30.
QEMU bundle `drtm-11.1.50-1` (11.1.50 (v11.1.0-1804-g8397ccc4b3)), swtpm 0.7.3.

Rows are the GRUB entries the suite boots, named as their fixtures
in `tests/conftest.py`, columns the releases. ✅ every test of the
entry passed, ❌ one failed, - nothing ran. A mark says what the
boot did, and the notes under the table what the suite expected of it.

## AMD SKINIT

### Without PSP, TPM with SHA-1 and SHA-256

| Entry                  | amd-drtm-test-image-4 | v0.5.2 | v0.5.3-rc1 |
|------------------------|-----------------------|--------|------------|
| `xen_efi_launch`       | ✅                     | ✅      | ✅          |
| `xen_efi`              | ✅                     | ✅      | ✅          |
| `xen_mb2_launch`       | ✅                     | ✅      | ✅          |
| `linux_launch`         | ✅                     | ❌      | ❌          |
| `linux_legacy_launch`  | ✅                     | ✅      | ✅          |
| `linux_alt_launch`     | ✅                     | ✅      | ✅          |
| `xen_efi_debug_launch` | ✅                     | ❌      | ❌          |
| `linux`                | ✅                     | ✅      | ✅          |

- `amd-drtm-test-image-4`: 124 passed.
- `v0.5.2`: 111 passed, 13 xfailed.
    - `linux_launch` expected: panics in check_timer: SKL entered startup_32, GIF never set
    - `xen_efi_debug_launch` expected: GRUB's debug print after exit_boot_services goes to the EFI console
- `v0.5.3-rc1`: 111 passed, 13 xfailed.
    - `linux_launch` expected: panics in check_timer: SKL entered startup_32, GIF never set
    - `xen_efi_debug_launch` expected: GRUB's debug print after exit_boot_services goes to the EFI console

<details>
<summary>Every test</summary>

| Test                                                                                              | amd-drtm-test-image-4 | v0.5.2  | v0.5.3-rc1 |
|---------------------------------------------------------------------------------------------------|-----------------------|---------|------------|
| `tests/test_console.py::test_a_dump_is_the_bytes_it_spells`                                       | passed                | passed  | passed     |
| `tests/test_console.py::test_the_newlines_a_long_dump_wraps_at_are_ignored`                       | passed                | passed  | passed     |
| `tests/test_console.py::test_a_hypervisor_line_spliced_into_a_dump_is_dropped`                    | passed                | passed  | passed     |
| `tests/test_console.py::test_a_hypervisor_line_spliced_into_the_middle_of_a_byte_is_dropped`      | passed                | passed  | passed     |
| `tests/test_console.py::test_a_dump_that_is_not_hex_still_raises`                                 | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_is_the_skls_events_then_xens`                           | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_header_declares_the_banks_in_its_order`                         | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[17-sha256]`                         | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[17-sha1]`                           | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[18-sha256]`                         | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[18-sha1]`                           | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_has_the_kernels_tags`                                 | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[17-sha256]` | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[17-sha1]`   | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[18-sha256]` | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[18-sha1]`   | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_zero_tail_of_the_log_region_is_not_an_event`                    | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_an_event_without_the_bank_leaves_that_banks_replay_alone`           | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_an_empty_or_foreign_buffer_is_refused`                              | passed                | passed  | passed     |
| `tests/test_grubcfg.py::test_entries_keep_their_commands_in_order_without_the_noise`              | passed                | passed  | passed     |
| `tests/test_grubcfg.py::test_the_parameter_lands_on_the_kernel_line_alone`                        | passed                | passed  | passed     |
| `tests/test_grubcfg.py::test_an_entry_without_a_kernel_line_is_refused`                           | passed                | passed  | passed     |
| `tests/test_grubcfg.py::test_the_boot_partition_is_the_efi_system_partition`                      | passed                | passed  | passed     |
| `tests/test_grubcfg.py::test_a_disk_without_one_is_refused`                                       | passed                | passed  | passed     |
| `tests/test_grubcfg.py::test_the_menu_is_read_in_the_environment_given`                           | passed                | passed  | passed     |
| `tests/test_launch.py::test_launch_extends_the_drtm_pcrs[xen_efi_launch]`                         | passed                | passed  | passed     |
| `tests/test_launch.py::test_launch_extends_the_drtm_pcrs[xen_mb2_launch]`                         | passed                | passed  | passed     |
| `tests/test_launch.py::test_launch_extends_the_drtm_pcrs[linux_launch]`                           | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_launch_extends_the_drtm_pcrs[linux_legacy_launch]`                    | passed                | passed  | passed     |
| `tests/test_launch.py::test_launch_extends_the_drtm_pcrs[linux_alt_launch]`                       | passed                | passed  | passed     |
| `tests/test_launch.py::test_launch_extends_the_drtm_pcrs[xen_efi_debug_launch]`                   | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_launch_brings_every_cpu_up[xen_efi_launch]`                           | passed                | passed  | passed     |
| `tests/test_launch.py::test_launch_brings_every_cpu_up[xen_mb2_launch]`                           | passed                | passed  | passed     |
| `tests/test_launch.py::test_launch_brings_every_cpu_up[linux_launch]`                             | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_launch_brings_every_cpu_up[linux_legacy_launch]`                      | passed                | passed  | passed     |
| `tests/test_launch.py::test_launch_brings_every_cpu_up[linux_alt_launch]`                         | passed                | passed  | passed     |
| `tests/test_launch.py::test_launch_brings_every_cpu_up[xen_efi_debug_launch]`                     | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_boot_shows_no_unexpected_errors[xen_efi_launch]`                      | passed                | passed  | passed     |
| `tests/test_launch.py::test_boot_shows_no_unexpected_errors[xen_efi]`                             | passed                | passed  | passed     |
| `tests/test_launch.py::test_boot_shows_no_unexpected_errors[xen_mb2_launch]`                      | passed                | passed  | passed     |
| `tests/test_launch.py::test_boot_shows_no_unexpected_errors[linux_launch]`                        | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_boot_shows_no_unexpected_errors[linux_legacy_launch]`                 | passed                | passed  | passed     |
| `tests/test_launch.py::test_boot_shows_no_unexpected_errors[linux_alt_launch]`                    | passed                | passed  | passed     |
| `tests/test_launch.py::test_boot_shows_no_unexpected_errors[xen_efi_debug_launch]`                | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_boot_shows_no_unexpected_errors[linux]`                               | passed                | passed  | passed     |
| `tests/test_linux.py::test_launch_is_recorded_by_the_platform`                                    | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_launch_is_seen_by_linux`                                               | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_launch_brings_the_iommu_up`                                            | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_launch_log_replays_to_the_pcrs`                                        | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_launch_log_declares_the_tpms_banks`                                    | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_legacy_launch_is_recorded_by_the_platform`                             | passed                | passed  | passed     |
| `tests/test_linux.py::test_legacy_launch_is_seen_by_linux`                                        | passed                | passed  | passed     |
| `tests/test_linux.py::test_legacy_launch_brings_the_iommu_up`                                     | passed                | passed  | passed     |
| `tests/test_linux.py::test_legacy_launch_log_replays_to_the_pcrs`                                 | passed                | passed  | passed     |
| `tests/test_linux.py::test_legacy_launch_log_declares_the_tpms_banks`                             | passed                | passed  | passed     |
| `tests/test_linux.py::test_alt_launch_is_recorded_by_the_platform`                                | passed                | passed  | passed     |
| `tests/test_linux.py::test_alt_launch_is_seen_by_linux`                                           | passed                | passed  | passed     |
| `tests/test_linux.py::test_alt_launch_log_replays_to_the_pcrs`                                    | passed                | passed  | passed     |
| `tests/test_linux.py::test_alt_launch_log_declares_the_tpms_banks`                                | passed                | passed  | passed     |
| `tests/test_linux.py::test_the_command_line_is_measured_into_pcr_18_alone`                        | passed                | passed  | passed     |
| `tests/test_linux.py::test_normal_boot_launches_nothing`                                          | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_workflow_gets_every_release_under_every_configuration`            | passed                | passed  | passed     |
| `tests/test_matrix.py::test_a_selection_of_releases_is_kept_in_the_order_given`                   | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env0-classic]`                | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env1-psp]`                    | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env2-sha256]`                 | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env3-psp-sha256]`             | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env4-sha384]`                 | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env5-psp]`                    | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env6-None]`                   | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env7-intel]`                  | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env8-intel-sha256]`           | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env9-intel-sha384]`           | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env10-None]`                  | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env11-classic]`               | passed                | passed  | passed     |
| `tests/test_matrix.py::test_a_cell_replaces_the_configuration_variables_and_the_local_image`      | passed                | passed  | passed     |
| `tests/test_menu.py::test_titles_come_out_in_menu_order_once_each`                                | passed                | passed  | passed     |
| `tests/test_menu.py::test_the_image_lists_every_entry_this_suite_knows`                           | passed                | passed  | passed     |
| `tests/test_qemu_binary.py::test_the_configured_binary_is_ours[amd]`                              | passed                | passed  | passed     |
| `tests/test_qemu_binary.py::test_the_configured_binary_is_ours[intel]`                            | passed                | passed  | passed     |
| `tests/test_qemu_binary.py::test_a_refused_option_is_reported`                                    | passed                | passed  | passed     |
| `tests/test_qemu_binary.py::test_a_warning_named_in_rejects_is_reported`                          | passed                | passed  | passed     |
| `tests/test_qemu_binary.py::test_a_missing_binary_is_reported`                                    | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_settings_hold_what_the_environment_said_when_read`                   | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_settings_carry_a_copy_of_the_environment`                            | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_settings_name_the_swtpm_programs_by_path`                            | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_settings_keep_a_missing_program_by_name`                             | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_a_vm_keeps_the_settings_it_was_made_with`                            | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_options_end_with_the_extra_arguments_given[extra0-expected0]`        | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_options_end_with_the_extra_arguments_given[extra1-expected1]`        | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_options_end_with_the_extra_arguments_given[None-expected2]`          | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_the_state_is_written_by_the_program_given`                           | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_the_program_runs_in_the_environment_given`                           | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_a_tpm_1_2_sits_behind_tis`                                           | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_a_tis_frontend_drops_the_hash_unless_told_not_to`                    | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_the_hash_drop_follows_the_environment[None-True]`                    | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_the_hash_drop_follows_the_environment[on-True]`                      | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_the_hash_drop_follows_the_environment[off-False]`                    | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_a_tpm_1_2_state_is_written_without_tpm2`                             | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_the_running_cpus_are_the_ones_not_halted`                            | passed                | passed  | passed     |
| `tests/test_report.py::test_a_cell_says_what_the_boot_did`                                        | passed                | passed  | passed     |
| `tests/test_report.py::test_the_notes_say_what_was_expected`                                      | passed                | passed  | passed     |
| `tests/test_report.py::test_a_release_without_results_is_a_missing_column`                        | passed                | passed  | passed     |
| `tests/test_report.py::test_the_full_table_has_every_test_and_the_parser_ones_only_there`         | passed                | passed  | passed     |
| `tests/test_report.py::test_the_sections_and_columns_follow_the_matrix_order`                     | passed                | passed  | passed     |
| `tests/test_report.py::test_the_header_names_the_commit_the_run_and_the_tools`                    | passed                | passed  | passed     |
| `tests/test_report.py::test_a_badge_is_green_only_when_every_configuration_passed`                | passed                | passed  | passed     |
| `tests/test_report.py::test_a_missing_configuration_alone_is_red_too`                             | passed                | passed  | passed     |
| `tests/test_report.py::test_a_hand_made_session_gets_a_section_of_its_own`                        | passed                | passed  | passed     |
| `tests/test_report.py::test_the_sections_are_grouped_by_vendor_amd_first`                         | passed                | passed  | passed     |
| `tests/test_report.py::test_main_reads_a_tree_of_results_and_writes_the_page_and_badges`          | passed                | passed  | passed     |
| `tests/test_xen.py::test_efi_launch_is_recorded_by_the_platform`                                  | passed                | passed  | passed     |
| `tests/test_xen.py::test_efi_launch_is_seen_by_xen`                                               | passed                | passed  | passed     |
| `tests/test_xen.py::test_efi_launch_brings_the_iommu_up`                                          | passed                | passed  | passed     |
| `tests/test_xen.py::test_efi_launch_log_replays_to_the_pcrs`                                      | passed                | passed  | passed     |
| `tests/test_xen.py::test_efi_launch_log_declares_the_tpms_banks`                                  | passed                | passed  | passed     |
| `tests/test_xen.py::test_efi_debug_launch_is_recorded_by_the_platform`                            | passed                | xfailed | xfailed    |
| `tests/test_xen.py::test_efi_debug_launch_prints_after_the_handover`                              | passed                | xfailed | xfailed    |
| `tests/test_xen.py::test_efi_normal_boot_launches_nothing`                                        | passed                | passed  | passed     |
| `tests/test_xen.py::test_mb2_launch_is_recorded_by_the_platform`                                  | passed                | passed  | passed     |
| `tests/test_xen.py::test_mb2_launch_is_seen_by_xen`                                               | passed                | passed  | passed     |
| `tests/test_xen.py::test_mb2_launch_brings_the_iommu_up`                                          | passed                | passed  | passed     |
| `tests/test_xen.py::test_mb2_launch_log_replays_to_the_pcrs`                                      | passed                | passed  | passed     |
| `tests/test_xen.py::test_mb2_launch_log_declares_the_tpms_banks`                                  | passed                | passed  | passed     |

</details>

### With PSP DRTM service, TPM with SHA-1 and SHA-256

| Entry                  | amd-drtm-test-image-4 | v0.5.2 | v0.5.3-rc1 |
|------------------------|-----------------------|--------|------------|
| `xen_efi_launch`       | ✅                     | ❌      | ❌          |
| `xen_efi`              | ✅                     | ✅      | ✅          |
| `xen_mb2_launch`       | ✅                     | ❌      | ❌          |
| `linux_launch`         | ✅                     | ❌      | ❌          |
| `linux_legacy_launch`  | ✅                     | ❌      | ❌          |
| `linux_alt_launch`     | ✅                     | ❌      | ❌          |
| `xen_efi_debug_launch` | ✅                     | ❌      | ❌          |
| `linux`                | ✅                     | ✅      | ✅          |

- `amd-drtm-test-image-4`: 123 passed, 1 skipped.
- `v0.5.2`: 89 passed, 1 skipped, 34 xfailed.
    - `xen_efi_launch` expected: classic SKL: no LAUNCH, so the PSP's locality locks stay on the TPM
    - `xen_mb2_launch` expected: classic SKL: no LAUNCH, so the PSP's locality locks stay on the TPM
    - `linux_launch` expected: classic SKL: the kernel's extend fails at a locked locality, it panics
    - `linux_legacy_launch` expected: classic SKL: the kernel's extend fails at a locked locality, it panics
    - `linux_alt_launch` expected: classic SKL: the kernel's extend fails at a locked locality, it panics
    - `xen_efi_debug_launch` expected: classic SKL: no LAUNCH, so the PSP's locality locks stay on the TPM
- `v0.5.3-rc1`: 89 passed, 1 skipped, 34 xfailed.
    - `xen_efi_launch` expected: classic SKL: no LAUNCH, so the PSP's locality locks stay on the TPM
    - `xen_mb2_launch` expected: classic SKL: no LAUNCH, so the PSP's locality locks stay on the TPM
    - `linux_launch` expected: classic SKL: the kernel's extend fails at a locked locality, it panics
    - `linux_legacy_launch` expected: classic SKL: the kernel's extend fails at a locked locality, it panics
    - `linux_alt_launch` expected: classic SKL: the kernel's extend fails at a locked locality, it panics
    - `xen_efi_debug_launch` expected: classic SKL: no LAUNCH, so the PSP's locality locks stay on the TPM

<details>
<summary>Every test</summary>

| Test                                                                                              | amd-drtm-test-image-4 | v0.5.2  | v0.5.3-rc1 |
|---------------------------------------------------------------------------------------------------|-----------------------|---------|------------|
| `tests/test_console.py::test_a_dump_is_the_bytes_it_spells`                                       | passed                | passed  | passed     |
| `tests/test_console.py::test_the_newlines_a_long_dump_wraps_at_are_ignored`                       | passed                | passed  | passed     |
| `tests/test_console.py::test_a_hypervisor_line_spliced_into_a_dump_is_dropped`                    | passed                | passed  | passed     |
| `tests/test_console.py::test_a_hypervisor_line_spliced_into_the_middle_of_a_byte_is_dropped`      | passed                | passed  | passed     |
| `tests/test_console.py::test_a_dump_that_is_not_hex_still_raises`                                 | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_is_the_skls_events_then_xens`                           | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_header_declares_the_banks_in_its_order`                         | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[17-sha256]`                         | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[17-sha1]`                           | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[18-sha256]`                         | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[18-sha1]`                           | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_has_the_kernels_tags`                                 | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[17-sha256]` | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[17-sha1]`   | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[18-sha256]` | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[18-sha1]`   | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_zero_tail_of_the_log_region_is_not_an_event`                    | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_an_event_without_the_bank_leaves_that_banks_replay_alone`           | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_an_empty_or_foreign_buffer_is_refused`                              | passed                | passed  | passed     |
| `tests/test_grubcfg.py::test_entries_keep_their_commands_in_order_without_the_noise`              | passed                | passed  | passed     |
| `tests/test_grubcfg.py::test_the_parameter_lands_on_the_kernel_line_alone`                        | passed                | passed  | passed     |
| `tests/test_grubcfg.py::test_an_entry_without_a_kernel_line_is_refused`                           | passed                | passed  | passed     |
| `tests/test_grubcfg.py::test_the_boot_partition_is_the_efi_system_partition`                      | passed                | passed  | passed     |
| `tests/test_grubcfg.py::test_a_disk_without_one_is_refused`                                       | passed                | passed  | passed     |
| `tests/test_grubcfg.py::test_the_menu_is_read_in_the_environment_given`                           | passed                | passed  | passed     |
| `tests/test_launch.py::test_launch_extends_the_drtm_pcrs[xen_efi_launch]`                         | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_launch_extends_the_drtm_pcrs[xen_mb2_launch]`                         | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_launch_extends_the_drtm_pcrs[linux_launch]`                           | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_launch_extends_the_drtm_pcrs[linux_legacy_launch]`                    | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_launch_extends_the_drtm_pcrs[linux_alt_launch]`                       | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_launch_extends_the_drtm_pcrs[xen_efi_debug_launch]`                   | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_launch_brings_every_cpu_up[xen_efi_launch]`                           | passed                | passed  | passed     |
| `tests/test_launch.py::test_launch_brings_every_cpu_up[xen_mb2_launch]`                           | passed                | passed  | passed     |
| `tests/test_launch.py::test_launch_brings_every_cpu_up[linux_launch]`                             | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_launch_brings_every_cpu_up[linux_legacy_launch]`                      | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_launch_brings_every_cpu_up[linux_alt_launch]`                         | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_launch_brings_every_cpu_up[xen_efi_debug_launch]`                     | passed                | passed  | passed     |
| `tests/test_launch.py::test_boot_shows_no_unexpected_errors[xen_efi_launch]`                      | passed                | passed  | passed     |
| `tests/test_launch.py::test_boot_shows_no_unexpected_errors[xen_efi]`                             | passed                | passed  | passed     |
| `tests/test_launch.py::test_boot_shows_no_unexpected_errors[xen_mb2_launch]`                      | passed                | passed  | passed     |
| `tests/test_launch.py::test_boot_shows_no_unexpected_errors[linux_launch]`                        | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_boot_shows_no_unexpected_errors[linux_legacy_launch]`                 | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_boot_shows_no_unexpected_errors[linux_alt_launch]`                    | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_boot_shows_no_unexpected_errors[xen_efi_debug_launch]`                | passed                | passed  | passed     |
| `tests/test_launch.py::test_boot_shows_no_unexpected_errors[linux]`                               | passed                | passed  | passed     |
| `tests/test_linux.py::test_launch_is_recorded_by_the_platform`                                    | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_launch_is_seen_by_linux`                                               | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_launch_brings_the_iommu_up`                                            | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_launch_log_replays_to_the_pcrs`                                        | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_launch_log_declares_the_tpms_banks`                                    | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_legacy_launch_is_recorded_by_the_platform`                             | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_legacy_launch_is_seen_by_linux`                                        | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_legacy_launch_brings_the_iommu_up`                                     | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_legacy_launch_log_replays_to_the_pcrs`                                 | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_legacy_launch_log_declares_the_tpms_banks`                             | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_alt_launch_is_recorded_by_the_platform`                                | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_alt_launch_is_seen_by_linux`                                           | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_alt_launch_log_replays_to_the_pcrs`                                    | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_alt_launch_log_declares_the_tpms_banks`                                | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_the_command_line_is_measured_into_pcr_18_alone`                        | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_normal_boot_launches_nothing`                                          | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_workflow_gets_every_release_under_every_configuration`            | passed                | passed  | passed     |
| `tests/test_matrix.py::test_a_selection_of_releases_is_kept_in_the_order_given`                   | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env0-classic]`                | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env1-psp]`                    | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env2-sha256]`                 | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env3-psp-sha256]`             | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env4-sha384]`                 | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env5-psp]`                    | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env6-None]`                   | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env7-intel]`                  | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env8-intel-sha256]`           | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env9-intel-sha384]`           | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env10-None]`                  | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env11-classic]`               | passed                | passed  | passed     |
| `tests/test_matrix.py::test_a_cell_replaces_the_configuration_variables_and_the_local_image`      | passed                | passed  | passed     |
| `tests/test_menu.py::test_titles_come_out_in_menu_order_once_each`                                | passed                | passed  | passed     |
| `tests/test_menu.py::test_the_image_lists_every_entry_this_suite_knows`                           | passed                | passed  | passed     |
| `tests/test_qemu_binary.py::test_the_configured_binary_is_ours[amd]`                              | passed                | passed  | passed     |
| `tests/test_qemu_binary.py::test_the_configured_binary_is_ours[intel]`                            | passed                | passed  | passed     |
| `tests/test_qemu_binary.py::test_a_refused_option_is_reported`                                    | passed                | passed  | passed     |
| `tests/test_qemu_binary.py::test_a_warning_named_in_rejects_is_reported`                          | passed                | passed  | passed     |
| `tests/test_qemu_binary.py::test_a_missing_binary_is_reported`                                    | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_settings_hold_what_the_environment_said_when_read`                   | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_settings_carry_a_copy_of_the_environment`                            | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_settings_name_the_swtpm_programs_by_path`                            | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_settings_keep_a_missing_program_by_name`                             | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_a_vm_keeps_the_settings_it_was_made_with`                            | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_options_end_with_the_extra_arguments_given[extra0-expected0]`        | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_options_end_with_the_extra_arguments_given[extra1-expected1]`        | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_options_end_with_the_extra_arguments_given[None-expected2]`          | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_the_state_is_written_by_the_program_given`                           | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_the_program_runs_in_the_environment_given`                           | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_a_tpm_1_2_sits_behind_tis`                                           | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_a_tis_frontend_drops_the_hash_unless_told_not_to`                    | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_the_hash_drop_follows_the_environment[None-True]`                    | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_the_hash_drop_follows_the_environment[on-True]`                      | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_the_hash_drop_follows_the_environment[off-False]`                    | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_a_tpm_1_2_state_is_written_without_tpm2`                             | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_the_running_cpus_are_the_ones_not_halted`                            | passed                | passed  | passed     |
| `tests/test_report.py::test_a_cell_says_what_the_boot_did`                                        | passed                | passed  | passed     |
| `tests/test_report.py::test_the_notes_say_what_was_expected`                                      | passed                | passed  | passed     |
| `tests/test_report.py::test_a_release_without_results_is_a_missing_column`                        | passed                | passed  | passed     |
| `tests/test_report.py::test_the_full_table_has_every_test_and_the_parser_ones_only_there`         | passed                | passed  | passed     |
| `tests/test_report.py::test_the_sections_and_columns_follow_the_matrix_order`                     | passed                | passed  | passed     |
| `tests/test_report.py::test_the_header_names_the_commit_the_run_and_the_tools`                    | passed                | passed  | passed     |
| `tests/test_report.py::test_a_badge_is_green_only_when_every_configuration_passed`                | passed                | passed  | passed     |
| `tests/test_report.py::test_a_missing_configuration_alone_is_red_too`                             | passed                | passed  | passed     |
| `tests/test_report.py::test_a_hand_made_session_gets_a_section_of_its_own`                        | passed                | passed  | passed     |
| `tests/test_report.py::test_the_sections_are_grouped_by_vendor_amd_first`                         | passed                | passed  | passed     |
| `tests/test_report.py::test_main_reads_a_tree_of_results_and_writes_the_page_and_badges`          | passed                | passed  | passed     |
| `tests/test_xen.py::test_efi_launch_is_recorded_by_the_platform`                                  | passed                | xfailed | xfailed    |
| `tests/test_xen.py::test_efi_launch_is_seen_by_xen`                                               | passed                | xfailed | xfailed    |
| `tests/test_xen.py::test_efi_launch_brings_the_iommu_up`                                          | passed                | passed  | passed     |
| `tests/test_xen.py::test_efi_launch_log_replays_to_the_pcrs`                                      | passed                | xfailed | xfailed    |
| `tests/test_xen.py::test_efi_launch_log_declares_the_tpms_banks`                                  | passed                | passed  | passed     |
| `tests/test_xen.py::test_efi_debug_launch_is_recorded_by_the_platform`                            | passed                | xfailed | xfailed    |
| `tests/test_xen.py::test_efi_debug_launch_prints_after_the_handover`                              | skipped               | skipped | skipped    |
| `tests/test_xen.py::test_efi_normal_boot_launches_nothing`                                        | passed                | passed  | passed     |
| `tests/test_xen.py::test_mb2_launch_is_recorded_by_the_platform`                                  | passed                | xfailed | xfailed    |
| `tests/test_xen.py::test_mb2_launch_is_seen_by_xen`                                               | passed                | xfailed | xfailed    |
| `tests/test_xen.py::test_mb2_launch_brings_the_iommu_up`                                          | passed                | passed  | passed     |
| `tests/test_xen.py::test_mb2_launch_log_replays_to_the_pcrs`                                      | passed                | xfailed | xfailed    |
| `tests/test_xen.py::test_mb2_launch_log_declares_the_tpms_banks`                                  | passed                | passed  | passed     |

</details>

### Without PSP, TPM with SHA-256 alone

| Entry                  | amd-drtm-test-image-4 | v0.5.2 | v0.5.3-rc1 |
|------------------------|-----------------------|--------|------------|
| `xen_efi_launch`       | ✅                     | ❌      | ❌          |
| `xen_efi`              | ✅                     | ✅      | ✅          |
| `xen_mb2_launch`       | ✅                     | ❌      | ❌          |
| `linux_launch`         | ✅                     | ❌      | ❌          |
| `linux_legacy_launch`  | ✅                     | ❌      | ❌          |
| `linux_alt_launch`     | ✅                     | ❌      | ❌          |
| `xen_efi_debug_launch` | ✅                     | ❌      | ❌          |
| `linux`                | ✅                     | ✅      | ✅          |

- `amd-drtm-test-image-4`: 124 passed.
- `v0.5.2`: 93 passed, 31 xfailed.
    - `xen_efi_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has
    - `xen_mb2_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has
    - `linux_launch` expected: panics in check_timer: SKL entered startup_32, GIF never set
    - `linux_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has
    - `linux_legacy_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has
    - `linux_alt_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has
    - `xen_efi_debug_launch` expected: GRUB's debug print after exit_boot_services goes to the EFI console
- `v0.5.3-rc1`: 93 passed, 31 xfailed.
    - `xen_efi_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has
    - `xen_mb2_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has
    - `linux_launch` expected: panics in check_timer: SKL entered startup_32, GIF never set
    - `linux_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has
    - `linux_legacy_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has
    - `linux_alt_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has
    - `xen_efi_debug_launch` expected: GRUB's debug print after exit_boot_services goes to the EFI console

<details>
<summary>Every test</summary>

| Test                                                                                              | amd-drtm-test-image-4 | v0.5.2  | v0.5.3-rc1 |
|---------------------------------------------------------------------------------------------------|-----------------------|---------|------------|
| `tests/test_console.py::test_a_dump_is_the_bytes_it_spells`                                       | passed                | passed  | passed     |
| `tests/test_console.py::test_the_newlines_a_long_dump_wraps_at_are_ignored`                       | passed                | passed  | passed     |
| `tests/test_console.py::test_a_hypervisor_line_spliced_into_a_dump_is_dropped`                    | passed                | passed  | passed     |
| `tests/test_console.py::test_a_hypervisor_line_spliced_into_the_middle_of_a_byte_is_dropped`      | passed                | passed  | passed     |
| `tests/test_console.py::test_a_dump_that_is_not_hex_still_raises`                                 | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_is_the_skls_events_then_xens`                           | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_header_declares_the_banks_in_its_order`                         | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[17-sha256]`                         | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[17-sha1]`                           | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[18-sha256]`                         | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[18-sha1]`                           | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_has_the_kernels_tags`                                 | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[17-sha256]` | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[17-sha1]`   | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[18-sha256]` | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[18-sha1]`   | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_zero_tail_of_the_log_region_is_not_an_event`                    | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_an_event_without_the_bank_leaves_that_banks_replay_alone`           | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_an_empty_or_foreign_buffer_is_refused`                              | passed                | passed  | passed     |
| `tests/test_grubcfg.py::test_entries_keep_their_commands_in_order_without_the_noise`              | passed                | passed  | passed     |
| `tests/test_grubcfg.py::test_the_parameter_lands_on_the_kernel_line_alone`                        | passed                | passed  | passed     |
| `tests/test_grubcfg.py::test_an_entry_without_a_kernel_line_is_refused`                           | passed                | passed  | passed     |
| `tests/test_grubcfg.py::test_the_boot_partition_is_the_efi_system_partition`                      | passed                | passed  | passed     |
| `tests/test_grubcfg.py::test_a_disk_without_one_is_refused`                                       | passed                | passed  | passed     |
| `tests/test_grubcfg.py::test_the_menu_is_read_in_the_environment_given`                           | passed                | passed  | passed     |
| `tests/test_launch.py::test_launch_extends_the_drtm_pcrs[xen_efi_launch]`                         | passed                | passed  | passed     |
| `tests/test_launch.py::test_launch_extends_the_drtm_pcrs[xen_mb2_launch]`                         | passed                | passed  | passed     |
| `tests/test_launch.py::test_launch_extends_the_drtm_pcrs[linux_launch]`                           | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_launch_extends_the_drtm_pcrs[linux_legacy_launch]`                    | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_launch_extends_the_drtm_pcrs[linux_alt_launch]`                       | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_launch_extends_the_drtm_pcrs[xen_efi_debug_launch]`                   | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_launch_brings_every_cpu_up[xen_efi_launch]`                           | passed                | passed  | passed     |
| `tests/test_launch.py::test_launch_brings_every_cpu_up[xen_mb2_launch]`                           | passed                | passed  | passed     |
| `tests/test_launch.py::test_launch_brings_every_cpu_up[linux_launch]`                             | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_launch_brings_every_cpu_up[linux_legacy_launch]`                      | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_launch_brings_every_cpu_up[linux_alt_launch]`                         | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_launch_brings_every_cpu_up[xen_efi_debug_launch]`                     | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_boot_shows_no_unexpected_errors[xen_efi_launch]`                      | passed                | passed  | passed     |
| `tests/test_launch.py::test_boot_shows_no_unexpected_errors[xen_efi]`                             | passed                | passed  | passed     |
| `tests/test_launch.py::test_boot_shows_no_unexpected_errors[xen_mb2_launch]`                      | passed                | passed  | passed     |
| `tests/test_launch.py::test_boot_shows_no_unexpected_errors[linux_launch]`                        | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_boot_shows_no_unexpected_errors[linux_legacy_launch]`                 | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_boot_shows_no_unexpected_errors[linux_alt_launch]`                    | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_boot_shows_no_unexpected_errors[xen_efi_debug_launch]`                | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_boot_shows_no_unexpected_errors[linux]`                               | passed                | passed  | passed     |
| `tests/test_linux.py::test_launch_is_recorded_by_the_platform`                                    | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_launch_is_seen_by_linux`                                               | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_launch_brings_the_iommu_up`                                            | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_launch_log_replays_to_the_pcrs`                                        | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_launch_log_declares_the_tpms_banks`                                    | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_legacy_launch_is_recorded_by_the_platform`                             | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_legacy_launch_is_seen_by_linux`                                        | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_legacy_launch_brings_the_iommu_up`                                     | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_legacy_launch_log_replays_to_the_pcrs`                                 | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_legacy_launch_log_declares_the_tpms_banks`                             | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_alt_launch_is_recorded_by_the_platform`                                | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_alt_launch_is_seen_by_linux`                                           | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_alt_launch_log_replays_to_the_pcrs`                                    | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_alt_launch_log_declares_the_tpms_banks`                                | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_the_command_line_is_measured_into_pcr_18_alone`                        | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_normal_boot_launches_nothing`                                          | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_workflow_gets_every_release_under_every_configuration`            | passed                | passed  | passed     |
| `tests/test_matrix.py::test_a_selection_of_releases_is_kept_in_the_order_given`                   | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env0-classic]`                | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env1-psp]`                    | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env2-sha256]`                 | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env3-psp-sha256]`             | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env4-sha384]`                 | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env5-psp]`                    | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env6-None]`                   | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env7-intel]`                  | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env8-intel-sha256]`           | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env9-intel-sha384]`           | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env10-None]`                  | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env11-classic]`               | passed                | passed  | passed     |
| `tests/test_matrix.py::test_a_cell_replaces_the_configuration_variables_and_the_local_image`      | passed                | passed  | passed     |
| `tests/test_menu.py::test_titles_come_out_in_menu_order_once_each`                                | passed                | passed  | passed     |
| `tests/test_menu.py::test_the_image_lists_every_entry_this_suite_knows`                           | passed                | passed  | passed     |
| `tests/test_qemu_binary.py::test_the_configured_binary_is_ours[amd]`                              | passed                | passed  | passed     |
| `tests/test_qemu_binary.py::test_the_configured_binary_is_ours[intel]`                            | passed                | passed  | passed     |
| `tests/test_qemu_binary.py::test_a_refused_option_is_reported`                                    | passed                | passed  | passed     |
| `tests/test_qemu_binary.py::test_a_warning_named_in_rejects_is_reported`                          | passed                | passed  | passed     |
| `tests/test_qemu_binary.py::test_a_missing_binary_is_reported`                                    | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_settings_hold_what_the_environment_said_when_read`                   | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_settings_carry_a_copy_of_the_environment`                            | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_settings_name_the_swtpm_programs_by_path`                            | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_settings_keep_a_missing_program_by_name`                             | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_a_vm_keeps_the_settings_it_was_made_with`                            | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_options_end_with_the_extra_arguments_given[extra0-expected0]`        | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_options_end_with_the_extra_arguments_given[extra1-expected1]`        | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_options_end_with_the_extra_arguments_given[None-expected2]`          | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_the_state_is_written_by_the_program_given`                           | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_the_program_runs_in_the_environment_given`                           | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_a_tpm_1_2_sits_behind_tis`                                           | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_a_tis_frontend_drops_the_hash_unless_told_not_to`                    | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_the_hash_drop_follows_the_environment[None-True]`                    | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_the_hash_drop_follows_the_environment[on-True]`                      | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_the_hash_drop_follows_the_environment[off-False]`                    | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_a_tpm_1_2_state_is_written_without_tpm2`                             | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_the_running_cpus_are_the_ones_not_halted`                            | passed                | passed  | passed     |
| `tests/test_report.py::test_a_cell_says_what_the_boot_did`                                        | passed                | passed  | passed     |
| `tests/test_report.py::test_the_notes_say_what_was_expected`                                      | passed                | passed  | passed     |
| `tests/test_report.py::test_a_release_without_results_is_a_missing_column`                        | passed                | passed  | passed     |
| `tests/test_report.py::test_the_full_table_has_every_test_and_the_parser_ones_only_there`         | passed                | passed  | passed     |
| `tests/test_report.py::test_the_sections_and_columns_follow_the_matrix_order`                     | passed                | passed  | passed     |
| `tests/test_report.py::test_the_header_names_the_commit_the_run_and_the_tools`                    | passed                | passed  | passed     |
| `tests/test_report.py::test_a_badge_is_green_only_when_every_configuration_passed`                | passed                | passed  | passed     |
| `tests/test_report.py::test_a_missing_configuration_alone_is_red_too`                             | passed                | passed  | passed     |
| `tests/test_report.py::test_a_hand_made_session_gets_a_section_of_its_own`                        | passed                | passed  | passed     |
| `tests/test_report.py::test_the_sections_are_grouped_by_vendor_amd_first`                         | passed                | passed  | passed     |
| `tests/test_report.py::test_main_reads_a_tree_of_results_and_writes_the_page_and_badges`          | passed                | passed  | passed     |
| `tests/test_xen.py::test_efi_launch_is_recorded_by_the_platform`                                  | passed                | passed  | passed     |
| `tests/test_xen.py::test_efi_launch_is_seen_by_xen`                                               | passed                | passed  | passed     |
| `tests/test_xen.py::test_efi_launch_brings_the_iommu_up`                                          | passed                | passed  | passed     |
| `tests/test_xen.py::test_efi_launch_log_replays_to_the_pcrs`                                      | passed                | passed  | passed     |
| `tests/test_xen.py::test_efi_launch_log_declares_the_tpms_banks`                                  | passed                | xfailed | xfailed    |
| `tests/test_xen.py::test_efi_debug_launch_is_recorded_by_the_platform`                            | passed                | xfailed | xfailed    |
| `tests/test_xen.py::test_efi_debug_launch_prints_after_the_handover`                              | passed                | xfailed | xfailed    |
| `tests/test_xen.py::test_efi_normal_boot_launches_nothing`                                        | passed                | passed  | passed     |
| `tests/test_xen.py::test_mb2_launch_is_recorded_by_the_platform`                                  | passed                | passed  | passed     |
| `tests/test_xen.py::test_mb2_launch_is_seen_by_xen`                                               | passed                | passed  | passed     |
| `tests/test_xen.py::test_mb2_launch_brings_the_iommu_up`                                          | passed                | passed  | passed     |
| `tests/test_xen.py::test_mb2_launch_log_replays_to_the_pcrs`                                      | passed                | passed  | passed     |
| `tests/test_xen.py::test_mb2_launch_log_declares_the_tpms_banks`                                  | passed                | xfailed | xfailed    |

</details>

### With PSP DRTM service, TPM with SHA-256 alone

| Entry                  | amd-drtm-test-image-4 | v0.5.2 | v0.5.3-rc1 |
|------------------------|-----------------------|--------|------------|
| `xen_efi_launch`       | ✅                     | ❌      | ❌          |
| `xen_efi`              | ✅                     | ✅      | ✅          |
| `xen_mb2_launch`       | ✅                     | ❌      | ❌          |
| `linux_launch`         | ✅                     | ❌      | ❌          |
| `linux_legacy_launch`  | ✅                     | ❌      | ❌          |
| `linux_alt_launch`     | ✅                     | ❌      | ❌          |
| `xen_efi_debug_launch` | ✅                     | ❌      | ❌          |
| `linux`                | ✅                     | ✅      | ✅          |

- `amd-drtm-test-image-4`: 123 passed, 1 skipped.
- `v0.5.2`: 87 passed, 1 skipped, 36 xfailed.
    - `xen_efi_launch` expected: classic SKL: no LAUNCH, so the PSP's locality locks stay on the TPM
    - `xen_efi_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has
    - `xen_mb2_launch` expected: classic SKL: no LAUNCH, so the PSP's locality locks stay on the TPM
    - `xen_mb2_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has
    - `linux_launch` expected: classic SKL: the kernel's extend fails at a locked locality, it panics
    - `linux_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has
    - `linux_legacy_launch` expected: classic SKL: the kernel's extend fails at a locked locality, it panics
    - `linux_legacy_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has
    - `linux_alt_launch` expected: classic SKL: the kernel's extend fails at a locked locality, it panics
    - `linux_alt_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has
    - `xen_efi_debug_launch` expected: classic SKL: no LAUNCH, so the PSP's locality locks stay on the TPM
- `v0.5.3-rc1`: 87 passed, 1 skipped, 36 xfailed.
    - `xen_efi_launch` expected: classic SKL: no LAUNCH, so the PSP's locality locks stay on the TPM
    - `xen_efi_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has
    - `xen_mb2_launch` expected: classic SKL: no LAUNCH, so the PSP's locality locks stay on the TPM
    - `xen_mb2_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has
    - `linux_launch` expected: classic SKL: the kernel's extend fails at a locked locality, it panics
    - `linux_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has
    - `linux_legacy_launch` expected: classic SKL: the kernel's extend fails at a locked locality, it panics
    - `linux_legacy_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has
    - `linux_alt_launch` expected: classic SKL: the kernel's extend fails at a locked locality, it panics
    - `linux_alt_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has
    - `xen_efi_debug_launch` expected: classic SKL: no LAUNCH, so the PSP's locality locks stay on the TPM

<details>
<summary>Every test</summary>

| Test                                                                                              | amd-drtm-test-image-4 | v0.5.2  | v0.5.3-rc1 |
|---------------------------------------------------------------------------------------------------|-----------------------|---------|------------|
| `tests/test_console.py::test_a_dump_is_the_bytes_it_spells`                                       | passed                | passed  | passed     |
| `tests/test_console.py::test_the_newlines_a_long_dump_wraps_at_are_ignored`                       | passed                | passed  | passed     |
| `tests/test_console.py::test_a_hypervisor_line_spliced_into_a_dump_is_dropped`                    | passed                | passed  | passed     |
| `tests/test_console.py::test_a_hypervisor_line_spliced_into_the_middle_of_a_byte_is_dropped`      | passed                | passed  | passed     |
| `tests/test_console.py::test_a_dump_that_is_not_hex_still_raises`                                 | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_is_the_skls_events_then_xens`                           | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_header_declares_the_banks_in_its_order`                         | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[17-sha256]`                         | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[17-sha1]`                           | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[18-sha256]`                         | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[18-sha1]`                           | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_has_the_kernels_tags`                                 | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[17-sha256]` | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[17-sha1]`   | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[18-sha256]` | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[18-sha1]`   | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_zero_tail_of_the_log_region_is_not_an_event`                    | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_an_event_without_the_bank_leaves_that_banks_replay_alone`           | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_an_empty_or_foreign_buffer_is_refused`                              | passed                | passed  | passed     |
| `tests/test_grubcfg.py::test_entries_keep_their_commands_in_order_without_the_noise`              | passed                | passed  | passed     |
| `tests/test_grubcfg.py::test_the_parameter_lands_on_the_kernel_line_alone`                        | passed                | passed  | passed     |
| `tests/test_grubcfg.py::test_an_entry_without_a_kernel_line_is_refused`                           | passed                | passed  | passed     |
| `tests/test_grubcfg.py::test_the_boot_partition_is_the_efi_system_partition`                      | passed                | passed  | passed     |
| `tests/test_grubcfg.py::test_a_disk_without_one_is_refused`                                       | passed                | passed  | passed     |
| `tests/test_grubcfg.py::test_the_menu_is_read_in_the_environment_given`                           | passed                | passed  | passed     |
| `tests/test_launch.py::test_launch_extends_the_drtm_pcrs[xen_efi_launch]`                         | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_launch_extends_the_drtm_pcrs[xen_mb2_launch]`                         | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_launch_extends_the_drtm_pcrs[linux_launch]`                           | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_launch_extends_the_drtm_pcrs[linux_legacy_launch]`                    | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_launch_extends_the_drtm_pcrs[linux_alt_launch]`                       | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_launch_extends_the_drtm_pcrs[xen_efi_debug_launch]`                   | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_launch_brings_every_cpu_up[xen_efi_launch]`                           | passed                | passed  | passed     |
| `tests/test_launch.py::test_launch_brings_every_cpu_up[xen_mb2_launch]`                           | passed                | passed  | passed     |
| `tests/test_launch.py::test_launch_brings_every_cpu_up[linux_launch]`                             | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_launch_brings_every_cpu_up[linux_legacy_launch]`                      | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_launch_brings_every_cpu_up[linux_alt_launch]`                         | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_launch_brings_every_cpu_up[xen_efi_debug_launch]`                     | passed                | passed  | passed     |
| `tests/test_launch.py::test_boot_shows_no_unexpected_errors[xen_efi_launch]`                      | passed                | passed  | passed     |
| `tests/test_launch.py::test_boot_shows_no_unexpected_errors[xen_efi]`                             | passed                | passed  | passed     |
| `tests/test_launch.py::test_boot_shows_no_unexpected_errors[xen_mb2_launch]`                      | passed                | passed  | passed     |
| `tests/test_launch.py::test_boot_shows_no_unexpected_errors[linux_launch]`                        | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_boot_shows_no_unexpected_errors[linux_legacy_launch]`                 | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_boot_shows_no_unexpected_errors[linux_alt_launch]`                    | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_boot_shows_no_unexpected_errors[xen_efi_debug_launch]`                | passed                | passed  | passed     |
| `tests/test_launch.py::test_boot_shows_no_unexpected_errors[linux]`                               | passed                | passed  | passed     |
| `tests/test_linux.py::test_launch_is_recorded_by_the_platform`                                    | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_launch_is_seen_by_linux`                                               | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_launch_brings_the_iommu_up`                                            | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_launch_log_replays_to_the_pcrs`                                        | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_launch_log_declares_the_tpms_banks`                                    | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_legacy_launch_is_recorded_by_the_platform`                             | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_legacy_launch_is_seen_by_linux`                                        | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_legacy_launch_brings_the_iommu_up`                                     | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_legacy_launch_log_replays_to_the_pcrs`                                 | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_legacy_launch_log_declares_the_tpms_banks`                             | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_alt_launch_is_recorded_by_the_platform`                                | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_alt_launch_is_seen_by_linux`                                           | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_alt_launch_log_replays_to_the_pcrs`                                    | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_alt_launch_log_declares_the_tpms_banks`                                | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_the_command_line_is_measured_into_pcr_18_alone`                        | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_normal_boot_launches_nothing`                                          | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_workflow_gets_every_release_under_every_configuration`            | passed                | passed  | passed     |
| `tests/test_matrix.py::test_a_selection_of_releases_is_kept_in_the_order_given`                   | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env0-classic]`                | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env1-psp]`                    | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env2-sha256]`                 | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env3-psp-sha256]`             | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env4-sha384]`                 | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env5-psp]`                    | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env6-None]`                   | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env7-intel]`                  | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env8-intel-sha256]`           | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env9-intel-sha384]`           | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env10-None]`                  | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env11-classic]`               | passed                | passed  | passed     |
| `tests/test_matrix.py::test_a_cell_replaces_the_configuration_variables_and_the_local_image`      | passed                | passed  | passed     |
| `tests/test_menu.py::test_titles_come_out_in_menu_order_once_each`                                | passed                | passed  | passed     |
| `tests/test_menu.py::test_the_image_lists_every_entry_this_suite_knows`                           | passed                | passed  | passed     |
| `tests/test_qemu_binary.py::test_the_configured_binary_is_ours[amd]`                              | passed                | passed  | passed     |
| `tests/test_qemu_binary.py::test_the_configured_binary_is_ours[intel]`                            | passed                | passed  | passed     |
| `tests/test_qemu_binary.py::test_a_refused_option_is_reported`                                    | passed                | passed  | passed     |
| `tests/test_qemu_binary.py::test_a_warning_named_in_rejects_is_reported`                          | passed                | passed  | passed     |
| `tests/test_qemu_binary.py::test_a_missing_binary_is_reported`                                    | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_settings_hold_what_the_environment_said_when_read`                   | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_settings_carry_a_copy_of_the_environment`                            | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_settings_name_the_swtpm_programs_by_path`                            | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_settings_keep_a_missing_program_by_name`                             | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_a_vm_keeps_the_settings_it_was_made_with`                            | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_options_end_with_the_extra_arguments_given[extra0-expected0]`        | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_options_end_with_the_extra_arguments_given[extra1-expected1]`        | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_options_end_with_the_extra_arguments_given[None-expected2]`          | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_the_state_is_written_by_the_program_given`                           | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_the_program_runs_in_the_environment_given`                           | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_a_tpm_1_2_sits_behind_tis`                                           | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_a_tis_frontend_drops_the_hash_unless_told_not_to`                    | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_the_hash_drop_follows_the_environment[None-True]`                    | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_the_hash_drop_follows_the_environment[on-True]`                      | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_the_hash_drop_follows_the_environment[off-False]`                    | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_a_tpm_1_2_state_is_written_without_tpm2`                             | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_the_running_cpus_are_the_ones_not_halted`                            | passed                | passed  | passed     |
| `tests/test_report.py::test_a_cell_says_what_the_boot_did`                                        | passed                | passed  | passed     |
| `tests/test_report.py::test_the_notes_say_what_was_expected`                                      | passed                | passed  | passed     |
| `tests/test_report.py::test_a_release_without_results_is_a_missing_column`                        | passed                | passed  | passed     |
| `tests/test_report.py::test_the_full_table_has_every_test_and_the_parser_ones_only_there`         | passed                | passed  | passed     |
| `tests/test_report.py::test_the_sections_and_columns_follow_the_matrix_order`                     | passed                | passed  | passed     |
| `tests/test_report.py::test_the_header_names_the_commit_the_run_and_the_tools`                    | passed                | passed  | passed     |
| `tests/test_report.py::test_a_badge_is_green_only_when_every_configuration_passed`                | passed                | passed  | passed     |
| `tests/test_report.py::test_a_missing_configuration_alone_is_red_too`                             | passed                | passed  | passed     |
| `tests/test_report.py::test_a_hand_made_session_gets_a_section_of_its_own`                        | passed                | passed  | passed     |
| `tests/test_report.py::test_the_sections_are_grouped_by_vendor_amd_first`                         | passed                | passed  | passed     |
| `tests/test_report.py::test_main_reads_a_tree_of_results_and_writes_the_page_and_badges`          | passed                | passed  | passed     |
| `tests/test_xen.py::test_efi_launch_is_recorded_by_the_platform`                                  | passed                | xfailed | xfailed    |
| `tests/test_xen.py::test_efi_launch_is_seen_by_xen`                                               | passed                | xfailed | xfailed    |
| `tests/test_xen.py::test_efi_launch_brings_the_iommu_up`                                          | passed                | passed  | passed     |
| `tests/test_xen.py::test_efi_launch_log_replays_to_the_pcrs`                                      | passed                | xfailed | xfailed    |
| `tests/test_xen.py::test_efi_launch_log_declares_the_tpms_banks`                                  | passed                | xfailed | xfailed    |
| `tests/test_xen.py::test_efi_debug_launch_is_recorded_by_the_platform`                            | passed                | xfailed | xfailed    |
| `tests/test_xen.py::test_efi_debug_launch_prints_after_the_handover`                              | skipped               | skipped | skipped    |
| `tests/test_xen.py::test_efi_normal_boot_launches_nothing`                                        | passed                | passed  | passed     |
| `tests/test_xen.py::test_mb2_launch_is_recorded_by_the_platform`                                  | passed                | xfailed | xfailed    |
| `tests/test_xen.py::test_mb2_launch_is_seen_by_xen`                                               | passed                | xfailed | xfailed    |
| `tests/test_xen.py::test_mb2_launch_brings_the_iommu_up`                                          | passed                | passed  | passed     |
| `tests/test_xen.py::test_mb2_launch_log_replays_to_the_pcrs`                                      | passed                | xfailed | xfailed    |
| `tests/test_xen.py::test_mb2_launch_log_declares_the_tpms_banks`                                  | passed                | xfailed | xfailed    |

</details>

### Without PSP, TPM with SHA-1, SHA-256 and SHA-384

| Entry                  | amd-drtm-test-image-4 | v0.5.2 | v0.5.3-rc1 |
|------------------------|-----------------------|--------|------------|
| `xen_efi_launch`       | ✅                     | ❌      | ❌          |
| `xen_efi`              | ✅                     | ✅      | ✅          |
| `xen_mb2_launch`       | ✅                     | ❌      | ❌          |
| `linux_launch`         | ✅                     | ❌      | ❌          |
| `linux_legacy_launch`  | ✅                     | ❌      | ❌          |
| `linux_alt_launch`     | ✅                     | ❌      | ❌          |
| `xen_efi_debug_launch` | ✅                     | ❌      | ❌          |
| `linux`                | ✅                     | ✅      | ✅          |

- `amd-drtm-test-image-4`: 124 passed.
- `v0.5.2`: 91 passed, 33 xfailed.
    - `xen_efi_launch` expected: the upstream Xen EFI launch extends PCR 18 in SHA-1 and SHA-256 alone
    - `xen_efi_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has
    - `xen_mb2_launch` expected: the upstream Xen copies the MBI's digests for SHA-1 and SHA-256 alone
    - `xen_mb2_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has
    - `linux_launch` expected: panics in check_timer: SKL entered startup_32, GIF never set
    - `linux_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has
    - `linux_legacy_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has
    - `linux_alt_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has
    - `xen_efi_debug_launch` expected: GRUB's debug print after exit_boot_services goes to the EFI console
- `v0.5.3-rc1`: 91 passed, 33 xfailed.
    - `xen_efi_launch` expected: the upstream Xen EFI launch extends PCR 18 in SHA-1 and SHA-256 alone
    - `xen_efi_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has
    - `xen_mb2_launch` expected: the upstream Xen copies the MBI's digests for SHA-1 and SHA-256 alone
    - `xen_mb2_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has
    - `linux_launch` expected: panics in check_timer: SKL entered startup_32, GIF never set
    - `linux_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has
    - `linux_legacy_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has
    - `linux_alt_launch` expected: the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has
    - `xen_efi_debug_launch` expected: GRUB's debug print after exit_boot_services goes to the EFI console

<details>
<summary>Every test</summary>

| Test                                                                                              | amd-drtm-test-image-4 | v0.5.2  | v0.5.3-rc1 |
|---------------------------------------------------------------------------------------------------|-----------------------|---------|------------|
| `tests/test_console.py::test_a_dump_is_the_bytes_it_spells`                                       | passed                | passed  | passed     |
| `tests/test_console.py::test_the_newlines_a_long_dump_wraps_at_are_ignored`                       | passed                | passed  | passed     |
| `tests/test_console.py::test_a_hypervisor_line_spliced_into_a_dump_is_dropped`                    | passed                | passed  | passed     |
| `tests/test_console.py::test_a_hypervisor_line_spliced_into_the_middle_of_a_byte_is_dropped`      | passed                | passed  | passed     |
| `tests/test_console.py::test_a_dump_that_is_not_hex_still_raises`                                 | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_is_the_skls_events_then_xens`                           | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_header_declares_the_banks_in_its_order`                         | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[17-sha256]`                         | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[17-sha1]`                           | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[18-sha256]`                         | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[18-sha1]`                           | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_has_the_kernels_tags`                                 | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[17-sha256]` | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[17-sha1]`   | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[18-sha256]` | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[18-sha1]`   | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_zero_tail_of_the_log_region_is_not_an_event`                    | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_an_event_without_the_bank_leaves_that_banks_replay_alone`           | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_an_empty_or_foreign_buffer_is_refused`                              | passed                | passed  | passed     |
| `tests/test_grubcfg.py::test_entries_keep_their_commands_in_order_without_the_noise`              | passed                | passed  | passed     |
| `tests/test_grubcfg.py::test_the_parameter_lands_on_the_kernel_line_alone`                        | passed                | passed  | passed     |
| `tests/test_grubcfg.py::test_an_entry_without_a_kernel_line_is_refused`                           | passed                | passed  | passed     |
| `tests/test_grubcfg.py::test_the_boot_partition_is_the_efi_system_partition`                      | passed                | passed  | passed     |
| `tests/test_grubcfg.py::test_a_disk_without_one_is_refused`                                       | passed                | passed  | passed     |
| `tests/test_grubcfg.py::test_the_menu_is_read_in_the_environment_given`                           | passed                | passed  | passed     |
| `tests/test_launch.py::test_launch_extends_the_drtm_pcrs[xen_efi_launch]`                         | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_launch_extends_the_drtm_pcrs[xen_mb2_launch]`                         | passed                | passed  | passed     |
| `tests/test_launch.py::test_launch_extends_the_drtm_pcrs[linux_launch]`                           | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_launch_extends_the_drtm_pcrs[linux_legacy_launch]`                    | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_launch_extends_the_drtm_pcrs[linux_alt_launch]`                       | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_launch_extends_the_drtm_pcrs[xen_efi_debug_launch]`                   | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_launch_brings_every_cpu_up[xen_efi_launch]`                           | passed                | passed  | passed     |
| `tests/test_launch.py::test_launch_brings_every_cpu_up[xen_mb2_launch]`                           | passed                | passed  | passed     |
| `tests/test_launch.py::test_launch_brings_every_cpu_up[linux_launch]`                             | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_launch_brings_every_cpu_up[linux_legacy_launch]`                      | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_launch_brings_every_cpu_up[linux_alt_launch]`                         | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_launch_brings_every_cpu_up[xen_efi_debug_launch]`                     | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_boot_shows_no_unexpected_errors[xen_efi_launch]`                      | passed                | passed  | passed     |
| `tests/test_launch.py::test_boot_shows_no_unexpected_errors[xen_efi]`                             | passed                | passed  | passed     |
| `tests/test_launch.py::test_boot_shows_no_unexpected_errors[xen_mb2_launch]`                      | passed                | passed  | passed     |
| `tests/test_launch.py::test_boot_shows_no_unexpected_errors[linux_launch]`                        | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_boot_shows_no_unexpected_errors[linux_legacy_launch]`                 | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_boot_shows_no_unexpected_errors[linux_alt_launch]`                    | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_boot_shows_no_unexpected_errors[xen_efi_debug_launch]`                | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_boot_shows_no_unexpected_errors[linux]`                               | passed                | passed  | passed     |
| `tests/test_linux.py::test_launch_is_recorded_by_the_platform`                                    | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_launch_is_seen_by_linux`                                               | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_launch_brings_the_iommu_up`                                            | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_launch_log_replays_to_the_pcrs`                                        | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_launch_log_declares_the_tpms_banks`                                    | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_legacy_launch_is_recorded_by_the_platform`                             | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_legacy_launch_is_seen_by_linux`                                        | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_legacy_launch_brings_the_iommu_up`                                     | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_legacy_launch_log_replays_to_the_pcrs`                                 | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_legacy_launch_log_declares_the_tpms_banks`                             | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_alt_launch_is_recorded_by_the_platform`                                | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_alt_launch_is_seen_by_linux`                                           | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_alt_launch_log_replays_to_the_pcrs`                                    | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_alt_launch_log_declares_the_tpms_banks`                                | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_the_command_line_is_measured_into_pcr_18_alone`                        | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_normal_boot_launches_nothing`                                          | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_workflow_gets_every_release_under_every_configuration`            | passed                | passed  | passed     |
| `tests/test_matrix.py::test_a_selection_of_releases_is_kept_in_the_order_given`                   | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env0-classic]`                | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env1-psp]`                    | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env2-sha256]`                 | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env3-psp-sha256]`             | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env4-sha384]`                 | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env5-psp]`                    | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env6-None]`                   | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env7-intel]`                  | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env8-intel-sha256]`           | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env9-intel-sha384]`           | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env10-None]`                  | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env11-classic]`               | passed                | passed  | passed     |
| `tests/test_matrix.py::test_a_cell_replaces_the_configuration_variables_and_the_local_image`      | passed                | passed  | passed     |
| `tests/test_menu.py::test_titles_come_out_in_menu_order_once_each`                                | passed                | passed  | passed     |
| `tests/test_menu.py::test_the_image_lists_every_entry_this_suite_knows`                           | passed                | passed  | passed     |
| `tests/test_qemu_binary.py::test_the_configured_binary_is_ours[amd]`                              | passed                | passed  | passed     |
| `tests/test_qemu_binary.py::test_the_configured_binary_is_ours[intel]`                            | passed                | passed  | passed     |
| `tests/test_qemu_binary.py::test_a_refused_option_is_reported`                                    | passed                | passed  | passed     |
| `tests/test_qemu_binary.py::test_a_warning_named_in_rejects_is_reported`                          | passed                | passed  | passed     |
| `tests/test_qemu_binary.py::test_a_missing_binary_is_reported`                                    | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_settings_hold_what_the_environment_said_when_read`                   | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_settings_carry_a_copy_of_the_environment`                            | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_settings_name_the_swtpm_programs_by_path`                            | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_settings_keep_a_missing_program_by_name`                             | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_a_vm_keeps_the_settings_it_was_made_with`                            | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_options_end_with_the_extra_arguments_given[extra0-expected0]`        | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_options_end_with_the_extra_arguments_given[extra1-expected1]`        | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_options_end_with_the_extra_arguments_given[None-expected2]`          | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_the_state_is_written_by_the_program_given`                           | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_the_program_runs_in_the_environment_given`                           | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_a_tpm_1_2_sits_behind_tis`                                           | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_a_tis_frontend_drops_the_hash_unless_told_not_to`                    | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_the_hash_drop_follows_the_environment[None-True]`                    | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_the_hash_drop_follows_the_environment[on-True]`                      | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_the_hash_drop_follows_the_environment[off-False]`                    | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_a_tpm_1_2_state_is_written_without_tpm2`                             | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_the_running_cpus_are_the_ones_not_halted`                            | passed                | passed  | passed     |
| `tests/test_report.py::test_a_cell_says_what_the_boot_did`                                        | passed                | passed  | passed     |
| `tests/test_report.py::test_the_notes_say_what_was_expected`                                      | passed                | passed  | passed     |
| `tests/test_report.py::test_a_release_without_results_is_a_missing_column`                        | passed                | passed  | passed     |
| `tests/test_report.py::test_the_full_table_has_every_test_and_the_parser_ones_only_there`         | passed                | passed  | passed     |
| `tests/test_report.py::test_the_sections_and_columns_follow_the_matrix_order`                     | passed                | passed  | passed     |
| `tests/test_report.py::test_the_header_names_the_commit_the_run_and_the_tools`                    | passed                | passed  | passed     |
| `tests/test_report.py::test_a_badge_is_green_only_when_every_configuration_passed`                | passed                | passed  | passed     |
| `tests/test_report.py::test_a_missing_configuration_alone_is_red_too`                             | passed                | passed  | passed     |
| `tests/test_report.py::test_a_hand_made_session_gets_a_section_of_its_own`                        | passed                | passed  | passed     |
| `tests/test_report.py::test_the_sections_are_grouped_by_vendor_amd_first`                         | passed                | passed  | passed     |
| `tests/test_report.py::test_main_reads_a_tree_of_results_and_writes_the_page_and_badges`          | passed                | passed  | passed     |
| `tests/test_xen.py::test_efi_launch_is_recorded_by_the_platform`                                  | passed                | passed  | passed     |
| `tests/test_xen.py::test_efi_launch_is_seen_by_xen`                                               | passed                | passed  | passed     |
| `tests/test_xen.py::test_efi_launch_brings_the_iommu_up`                                          | passed                | passed  | passed     |
| `tests/test_xen.py::test_efi_launch_log_replays_to_the_pcrs`                                      | passed                | passed  | passed     |
| `tests/test_xen.py::test_efi_launch_log_declares_the_tpms_banks`                                  | passed                | xfailed | xfailed    |
| `tests/test_xen.py::test_efi_debug_launch_is_recorded_by_the_platform`                            | passed                | xfailed | xfailed    |
| `tests/test_xen.py::test_efi_debug_launch_prints_after_the_handover`                              | passed                | xfailed | xfailed    |
| `tests/test_xen.py::test_efi_normal_boot_launches_nothing`                                        | passed                | passed  | passed     |
| `tests/test_xen.py::test_mb2_launch_is_recorded_by_the_platform`                                  | passed                | passed  | passed     |
| `tests/test_xen.py::test_mb2_launch_is_seen_by_xen`                                               | passed                | passed  | passed     |
| `tests/test_xen.py::test_mb2_launch_brings_the_iommu_up`                                          | passed                | passed  | passed     |
| `tests/test_xen.py::test_mb2_launch_log_replays_to_the_pcrs`                                      | passed                | xfailed | xfailed    |
| `tests/test_xen.py::test_mb2_launch_log_declares_the_tpms_banks`                                  | passed                | xfailed | xfailed    |

</details>

## Intel TXT

### TPM with SHA-1 and SHA-256

| Entry                 | amd-drtm-test-image-4 | v0.5.2 | v0.5.3-rc1 |
|-----------------------|-----------------------|--------|------------|
| `xen_efi_launch`      | ✅                     | ❌      | ❌          |
| `xen_efi`             | ✅                     | ✅      | ✅          |
| `xen_mb2_launch`      | ✅                     | ❌      | ❌          |
| `linux_launch`        | ✅                     | ❌      | ❌          |
| `linux_legacy_launch` | ❌                     | ❌      | ❌          |
| `linux_alt_launch`    | ❌                     | ❌      | ❌          |
| `linux`               | ✅                     | ✅      | ✅          |

- `amd-drtm-test-image-4`: 7 failed, 102 passed.
    - `linux_legacy_launch`: 7 failed unexpectedly
    - `linux_alt_launch`: 1 failed unexpectedly
- `v0.5.2`: 87 passed, 22 xfailed.
    - `xen_efi_launch` expected: the upstream Xen's MLE_JOIN has the GDT base as its limit
    - `xen_mb2_launch` expected: the upstream Xen's MLE_JOIN has the GDT base as its limit
    - `linux_launch` expected: the decompressor wipes boot_params the EFI stub placed there
    - `linux_legacy_launch` expected: no CONFIG_INTEL_IOMMU: the VT-d PMRs stay on and block the disk
    - `linux_alt_launch` expected: no CONFIG_INTEL_IOMMU: the VT-d PMRs stay on and block the disk
- `v0.5.3-rc1`: 87 passed, 22 xfailed.
    - `xen_efi_launch` expected: the upstream Xen's MLE_JOIN has the GDT base as its limit
    - `xen_mb2_launch` expected: the upstream Xen's MLE_JOIN has the GDT base as its limit
    - `linux_launch` expected: the decompressor wipes boot_params the EFI stub placed there
    - `linux_legacy_launch` expected: no CONFIG_INTEL_IOMMU: the VT-d PMRs stay on and block the disk
    - `linux_alt_launch` expected: no CONFIG_INTEL_IOMMU: the VT-d PMRs stay on and block the disk

<details>
<summary>Every test</summary>

| Test                                                                                              | amd-drtm-test-image-4 | v0.5.2  | v0.5.3-rc1 |
|---------------------------------------------------------------------------------------------------|-----------------------|---------|------------|
| `tests/test_console.py::test_a_dump_is_the_bytes_it_spells`                                       | passed                | passed  | passed     |
| `tests/test_console.py::test_the_newlines_a_long_dump_wraps_at_are_ignored`                       | passed                | passed  | passed     |
| `tests/test_console.py::test_a_hypervisor_line_spliced_into_a_dump_is_dropped`                    | passed                | passed  | passed     |
| `tests/test_console.py::test_a_hypervisor_line_spliced_into_the_middle_of_a_byte_is_dropped`      | passed                | passed  | passed     |
| `tests/test_console.py::test_a_dump_that_is_not_hex_still_raises`                                 | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_is_the_skls_events_then_xens`                           | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_header_declares_the_banks_in_its_order`                         | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[17-sha256]`                         | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[17-sha1]`                           | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[18-sha256]`                         | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[18-sha1]`                           | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_has_the_kernels_tags`                                 | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[17-sha256]` | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[17-sha1]`   | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[18-sha256]` | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[18-sha1]`   | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_zero_tail_of_the_log_region_is_not_an_event`                    | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_an_event_without_the_bank_leaves_that_banks_replay_alone`           | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_an_empty_or_foreign_buffer_is_refused`                              | passed                | passed  | passed     |
| `tests/test_grubcfg.py::test_entries_keep_their_commands_in_order_without_the_noise`              | passed                | passed  | passed     |
| `tests/test_grubcfg.py::test_the_parameter_lands_on_the_kernel_line_alone`                        | passed                | passed  | passed     |
| `tests/test_grubcfg.py::test_an_entry_without_a_kernel_line_is_refused`                           | passed                | passed  | passed     |
| `tests/test_grubcfg.py::test_the_boot_partition_is_the_efi_system_partition`                      | passed                | passed  | passed     |
| `tests/test_grubcfg.py::test_a_disk_without_one_is_refused`                                       | passed                | passed  | passed     |
| `tests/test_grubcfg.py::test_the_menu_is_read_in_the_environment_given`                           | passed                | passed  | passed     |
| `tests/test_launch.py::test_launch_extends_the_drtm_pcrs[xen_efi_launch]`                         | passed                | passed  | passed     |
| `tests/test_launch.py::test_launch_extends_the_drtm_pcrs[xen_mb2_launch]`                         | passed                | passed  | passed     |
| `tests/test_launch.py::test_launch_extends_the_drtm_pcrs[linux_launch]`                           | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_launch_extends_the_drtm_pcrs[linux_legacy_launch]`                    | failed                | xfailed | xfailed    |
| `tests/test_launch.py::test_launch_extends_the_drtm_pcrs[linux_alt_launch]`                       | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_launch_brings_every_cpu_up[xen_efi_launch]`                           | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_launch_brings_every_cpu_up[xen_mb2_launch]`                           | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_launch_brings_every_cpu_up[linux_launch]`                             | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_launch_brings_every_cpu_up[linux_legacy_launch]`                      | failed                | xfailed | xfailed    |
| `tests/test_launch.py::test_launch_brings_every_cpu_up[linux_alt_launch]`                         | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_boot_shows_no_unexpected_errors[xen_efi_launch]`                      | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_boot_shows_no_unexpected_errors[xen_efi]`                             | passed                | passed  | passed     |
| `tests/test_launch.py::test_boot_shows_no_unexpected_errors[xen_mb2_launch]`                      | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_boot_shows_no_unexpected_errors[linux_launch]`                        | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_boot_shows_no_unexpected_errors[linux_legacy_launch]`                 | failed                | xfailed | xfailed    |
| `tests/test_launch.py::test_boot_shows_no_unexpected_errors[linux_alt_launch]`                    | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_boot_shows_no_unexpected_errors[linux]`                               | passed                | passed  | passed     |
| `tests/test_linux.py::test_launch_is_seen_by_linux`                                               | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_launch_brings_the_iommu_up`                                            | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_launch_log_declares_the_tpms_banks`                                    | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_legacy_launch_is_seen_by_linux`                                        | failed                | xfailed | xfailed    |
| `tests/test_linux.py::test_legacy_launch_brings_the_iommu_up`                                     | failed                | xfailed | xfailed    |
| `tests/test_linux.py::test_legacy_launch_log_declares_the_tpms_banks`                             | failed                | xfailed | xfailed    |
| `tests/test_linux.py::test_alt_launch_is_seen_by_linux`                                           | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_alt_launch_log_declares_the_tpms_banks`                                | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_the_command_line_is_measured_into_pcr_18_alone`                        | failed                | xfailed | xfailed    |
| `tests/test_linux.py::test_normal_boot_launches_nothing`                                          | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_workflow_gets_every_release_under_every_configuration`            | passed                | passed  | passed     |
| `tests/test_matrix.py::test_a_selection_of_releases_is_kept_in_the_order_given`                   | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env0-classic]`                | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env1-psp]`                    | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env2-sha256]`                 | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env3-psp-sha256]`             | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env4-sha384]`                 | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env5-psp]`                    | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env6-None]`                   | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env7-intel]`                  | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env8-intel-sha256]`           | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env9-intel-sha384]`           | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env10-None]`                  | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env11-classic]`               | passed                | passed  | passed     |
| `tests/test_matrix.py::test_a_cell_replaces_the_configuration_variables_and_the_local_image`      | passed                | passed  | passed     |
| `tests/test_menu.py::test_titles_come_out_in_menu_order_once_each`                                | passed                | passed  | passed     |
| `tests/test_menu.py::test_the_image_lists_every_entry_this_suite_knows`                           | passed                | passed  | passed     |
| `tests/test_qemu_binary.py::test_the_configured_binary_is_ours[amd]`                              | passed                | passed  | passed     |
| `tests/test_qemu_binary.py::test_the_configured_binary_is_ours[intel]`                            | passed                | passed  | passed     |
| `tests/test_qemu_binary.py::test_a_refused_option_is_reported`                                    | passed                | passed  | passed     |
| `tests/test_qemu_binary.py::test_a_warning_named_in_rejects_is_reported`                          | passed                | passed  | passed     |
| `tests/test_qemu_binary.py::test_a_missing_binary_is_reported`                                    | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_settings_hold_what_the_environment_said_when_read`                   | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_settings_carry_a_copy_of_the_environment`                            | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_settings_name_the_swtpm_programs_by_path`                            | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_settings_keep_a_missing_program_by_name`                             | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_a_vm_keeps_the_settings_it_was_made_with`                            | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_options_end_with_the_extra_arguments_given[extra0-expected0]`        | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_options_end_with_the_extra_arguments_given[extra1-expected1]`        | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_options_end_with_the_extra_arguments_given[None-expected2]`          | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_the_state_is_written_by_the_program_given`                           | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_the_program_runs_in_the_environment_given`                           | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_a_tpm_1_2_sits_behind_tis`                                           | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_a_tis_frontend_drops_the_hash_unless_told_not_to`                    | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_the_hash_drop_follows_the_environment[None-True]`                    | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_the_hash_drop_follows_the_environment[on-True]`                      | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_the_hash_drop_follows_the_environment[off-False]`                    | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_a_tpm_1_2_state_is_written_without_tpm2`                             | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_the_running_cpus_are_the_ones_not_halted`                            | passed                | passed  | passed     |
| `tests/test_report.py::test_a_cell_says_what_the_boot_did`                                        | passed                | passed  | passed     |
| `tests/test_report.py::test_the_notes_say_what_was_expected`                                      | passed                | passed  | passed     |
| `tests/test_report.py::test_a_release_without_results_is_a_missing_column`                        | passed                | passed  | passed     |
| `tests/test_report.py::test_the_full_table_has_every_test_and_the_parser_ones_only_there`         | passed                | passed  | passed     |
| `tests/test_report.py::test_the_sections_and_columns_follow_the_matrix_order`                     | passed                | passed  | passed     |
| `tests/test_report.py::test_the_header_names_the_commit_the_run_and_the_tools`                    | passed                | passed  | passed     |
| `tests/test_report.py::test_a_badge_is_green_only_when_every_configuration_passed`                | passed                | passed  | passed     |
| `tests/test_report.py::test_a_missing_configuration_alone_is_red_too`                             | passed                | passed  | passed     |
| `tests/test_report.py::test_a_hand_made_session_gets_a_section_of_its_own`                        | passed                | passed  | passed     |
| `tests/test_report.py::test_the_sections_are_grouped_by_vendor_amd_first`                         | passed                | passed  | passed     |
| `tests/test_report.py::test_main_reads_a_tree_of_results_and_writes_the_page_and_badges`          | passed                | passed  | passed     |
| `tests/test_xen.py::test_efi_launch_is_seen_by_xen`                                               | passed                | passed  | passed     |
| `tests/test_xen.py::test_efi_launch_brings_the_iommu_up`                                          | passed                | passed  | passed     |
| `tests/test_xen.py::test_efi_launch_log_declares_the_tpms_banks`                                  | passed                | passed  | passed     |
| `tests/test_xen.py::test_efi_normal_boot_launches_nothing`                                        | passed                | passed  | passed     |
| `tests/test_xen.py::test_mb2_launch_is_seen_by_xen`                                               | passed                | passed  | passed     |
| `tests/test_xen.py::test_mb2_launch_brings_the_iommu_up`                                          | passed                | passed  | passed     |
| `tests/test_xen.py::test_mb2_launch_log_declares_the_tpms_banks`                                  | passed                | passed  | passed     |

</details>

### TPM with SHA-256 alone

| Entry                 | amd-drtm-test-image-4 | v0.5.2 | v0.5.3-rc1 |
|-----------------------|-----------------------|--------|------------|
| `xen_efi_launch`      | ✅                     | ❌      | ❌          |
| `xen_efi`             | ✅                     | ✅      | ✅          |
| `xen_mb2_launch`      | ✅                     | ❌      | ❌          |
| `linux_launch`        | ✅                     | ❌      | ❌          |
| `linux_legacy_launch` | ✅                     | ❌      | ❌          |
| `linux_alt_launch`    | ✅                     | ❌      | ❌          |
| `linux`               | ✅                     | ✅      | ✅          |

- `amd-drtm-test-image-4`: 109 passed.
- `v0.5.2`: 87 passed, 22 xfailed.
    - `xen_efi_launch` expected: the upstream Xen's MLE_JOIN has the GDT base as its limit
    - `xen_mb2_launch` expected: the upstream Xen's MLE_JOIN has the GDT base as its limit
    - `linux_launch` expected: the decompressor wipes boot_params the EFI stub placed there
    - `linux_legacy_launch` expected: no CONFIG_INTEL_IOMMU: the VT-d PMRs stay on and block the disk
    - `linux_alt_launch` expected: no CONFIG_INTEL_IOMMU: the VT-d PMRs stay on and block the disk
- `v0.5.3-rc1`: 87 passed, 22 xfailed.
    - `xen_efi_launch` expected: the upstream Xen's MLE_JOIN has the GDT base as its limit
    - `xen_mb2_launch` expected: the upstream Xen's MLE_JOIN has the GDT base as its limit
    - `linux_launch` expected: the decompressor wipes boot_params the EFI stub placed there
    - `linux_legacy_launch` expected: no CONFIG_INTEL_IOMMU: the VT-d PMRs stay on and block the disk
    - `linux_alt_launch` expected: no CONFIG_INTEL_IOMMU: the VT-d PMRs stay on and block the disk

<details>
<summary>Every test</summary>

| Test                                                                                              | amd-drtm-test-image-4 | v0.5.2  | v0.5.3-rc1 |
|---------------------------------------------------------------------------------------------------|-----------------------|---------|------------|
| `tests/test_console.py::test_a_dump_is_the_bytes_it_spells`                                       | passed                | passed  | passed     |
| `tests/test_console.py::test_the_newlines_a_long_dump_wraps_at_are_ignored`                       | passed                | passed  | passed     |
| `tests/test_console.py::test_a_hypervisor_line_spliced_into_a_dump_is_dropped`                    | passed                | passed  | passed     |
| `tests/test_console.py::test_a_hypervisor_line_spliced_into_the_middle_of_a_byte_is_dropped`      | passed                | passed  | passed     |
| `tests/test_console.py::test_a_dump_that_is_not_hex_still_raises`                                 | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_is_the_skls_events_then_xens`                           | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_header_declares_the_banks_in_its_order`                         | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[17-sha256]`                         | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[17-sha1]`                           | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[18-sha256]`                         | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[18-sha1]`                           | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_has_the_kernels_tags`                                 | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[17-sha256]` | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[17-sha1]`   | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[18-sha256]` | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[18-sha1]`   | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_zero_tail_of_the_log_region_is_not_an_event`                    | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_an_event_without_the_bank_leaves_that_banks_replay_alone`           | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_an_empty_or_foreign_buffer_is_refused`                              | passed                | passed  | passed     |
| `tests/test_grubcfg.py::test_entries_keep_their_commands_in_order_without_the_noise`              | passed                | passed  | passed     |
| `tests/test_grubcfg.py::test_the_parameter_lands_on_the_kernel_line_alone`                        | passed                | passed  | passed     |
| `tests/test_grubcfg.py::test_an_entry_without_a_kernel_line_is_refused`                           | passed                | passed  | passed     |
| `tests/test_grubcfg.py::test_the_boot_partition_is_the_efi_system_partition`                      | passed                | passed  | passed     |
| `tests/test_grubcfg.py::test_a_disk_without_one_is_refused`                                       | passed                | passed  | passed     |
| `tests/test_grubcfg.py::test_the_menu_is_read_in_the_environment_given`                           | passed                | passed  | passed     |
| `tests/test_launch.py::test_launch_extends_the_drtm_pcrs[xen_efi_launch]`                         | passed                | passed  | passed     |
| `tests/test_launch.py::test_launch_extends_the_drtm_pcrs[xen_mb2_launch]`                         | passed                | passed  | passed     |
| `tests/test_launch.py::test_launch_extends_the_drtm_pcrs[linux_launch]`                           | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_launch_extends_the_drtm_pcrs[linux_legacy_launch]`                    | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_launch_extends_the_drtm_pcrs[linux_alt_launch]`                       | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_launch_brings_every_cpu_up[xen_efi_launch]`                           | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_launch_brings_every_cpu_up[xen_mb2_launch]`                           | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_launch_brings_every_cpu_up[linux_launch]`                             | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_launch_brings_every_cpu_up[linux_legacy_launch]`                      | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_launch_brings_every_cpu_up[linux_alt_launch]`                         | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_boot_shows_no_unexpected_errors[xen_efi_launch]`                      | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_boot_shows_no_unexpected_errors[xen_efi]`                             | passed                | passed  | passed     |
| `tests/test_launch.py::test_boot_shows_no_unexpected_errors[xen_mb2_launch]`                      | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_boot_shows_no_unexpected_errors[linux_launch]`                        | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_boot_shows_no_unexpected_errors[linux_legacy_launch]`                 | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_boot_shows_no_unexpected_errors[linux_alt_launch]`                    | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_boot_shows_no_unexpected_errors[linux]`                               | passed                | passed  | passed     |
| `tests/test_linux.py::test_launch_is_seen_by_linux`                                               | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_launch_brings_the_iommu_up`                                            | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_launch_log_declares_the_tpms_banks`                                    | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_legacy_launch_is_seen_by_linux`                                        | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_legacy_launch_brings_the_iommu_up`                                     | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_legacy_launch_log_declares_the_tpms_banks`                             | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_alt_launch_is_seen_by_linux`                                           | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_alt_launch_log_declares_the_tpms_banks`                                | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_the_command_line_is_measured_into_pcr_18_alone`                        | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_normal_boot_launches_nothing`                                          | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_workflow_gets_every_release_under_every_configuration`            | passed                | passed  | passed     |
| `tests/test_matrix.py::test_a_selection_of_releases_is_kept_in_the_order_given`                   | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env0-classic]`                | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env1-psp]`                    | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env2-sha256]`                 | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env3-psp-sha256]`             | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env4-sha384]`                 | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env5-psp]`                    | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env6-None]`                   | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env7-intel]`                  | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env8-intel-sha256]`           | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env9-intel-sha384]`           | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env10-None]`                  | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env11-classic]`               | passed                | passed  | passed     |
| `tests/test_matrix.py::test_a_cell_replaces_the_configuration_variables_and_the_local_image`      | passed                | passed  | passed     |
| `tests/test_menu.py::test_titles_come_out_in_menu_order_once_each`                                | passed                | passed  | passed     |
| `tests/test_menu.py::test_the_image_lists_every_entry_this_suite_knows`                           | passed                | passed  | passed     |
| `tests/test_qemu_binary.py::test_the_configured_binary_is_ours[amd]`                              | passed                | passed  | passed     |
| `tests/test_qemu_binary.py::test_the_configured_binary_is_ours[intel]`                            | passed                | passed  | passed     |
| `tests/test_qemu_binary.py::test_a_refused_option_is_reported`                                    | passed                | passed  | passed     |
| `tests/test_qemu_binary.py::test_a_warning_named_in_rejects_is_reported`                          | passed                | passed  | passed     |
| `tests/test_qemu_binary.py::test_a_missing_binary_is_reported`                                    | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_settings_hold_what_the_environment_said_when_read`                   | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_settings_carry_a_copy_of_the_environment`                            | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_settings_name_the_swtpm_programs_by_path`                            | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_settings_keep_a_missing_program_by_name`                             | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_a_vm_keeps_the_settings_it_was_made_with`                            | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_options_end_with_the_extra_arguments_given[extra0-expected0]`        | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_options_end_with_the_extra_arguments_given[extra1-expected1]`        | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_options_end_with_the_extra_arguments_given[None-expected2]`          | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_the_state_is_written_by_the_program_given`                           | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_the_program_runs_in_the_environment_given`                           | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_a_tpm_1_2_sits_behind_tis`                                           | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_a_tis_frontend_drops_the_hash_unless_told_not_to`                    | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_the_hash_drop_follows_the_environment[None-True]`                    | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_the_hash_drop_follows_the_environment[on-True]`                      | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_the_hash_drop_follows_the_environment[off-False]`                    | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_a_tpm_1_2_state_is_written_without_tpm2`                             | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_the_running_cpus_are_the_ones_not_halted`                            | passed                | passed  | passed     |
| `tests/test_report.py::test_a_cell_says_what_the_boot_did`                                        | passed                | passed  | passed     |
| `tests/test_report.py::test_the_notes_say_what_was_expected`                                      | passed                | passed  | passed     |
| `tests/test_report.py::test_a_release_without_results_is_a_missing_column`                        | passed                | passed  | passed     |
| `tests/test_report.py::test_the_full_table_has_every_test_and_the_parser_ones_only_there`         | passed                | passed  | passed     |
| `tests/test_report.py::test_the_sections_and_columns_follow_the_matrix_order`                     | passed                | passed  | passed     |
| `tests/test_report.py::test_the_header_names_the_commit_the_run_and_the_tools`                    | passed                | passed  | passed     |
| `tests/test_report.py::test_a_badge_is_green_only_when_every_configuration_passed`                | passed                | passed  | passed     |
| `tests/test_report.py::test_a_missing_configuration_alone_is_red_too`                             | passed                | passed  | passed     |
| `tests/test_report.py::test_a_hand_made_session_gets_a_section_of_its_own`                        | passed                | passed  | passed     |
| `tests/test_report.py::test_the_sections_are_grouped_by_vendor_amd_first`                         | passed                | passed  | passed     |
| `tests/test_report.py::test_main_reads_a_tree_of_results_and_writes_the_page_and_badges`          | passed                | passed  | passed     |
| `tests/test_xen.py::test_efi_launch_is_seen_by_xen`                                               | passed                | passed  | passed     |
| `tests/test_xen.py::test_efi_launch_brings_the_iommu_up`                                          | passed                | passed  | passed     |
| `tests/test_xen.py::test_efi_launch_log_declares_the_tpms_banks`                                  | passed                | passed  | passed     |
| `tests/test_xen.py::test_efi_normal_boot_launches_nothing`                                        | passed                | passed  | passed     |
| `tests/test_xen.py::test_mb2_launch_is_seen_by_xen`                                               | passed                | passed  | passed     |
| `tests/test_xen.py::test_mb2_launch_brings_the_iommu_up`                                          | passed                | passed  | passed     |
| `tests/test_xen.py::test_mb2_launch_log_declares_the_tpms_banks`                                  | passed                | passed  | passed     |

</details>

### TPM with SHA-1, SHA-256 and SHA-384

| Entry                 | amd-drtm-test-image-4 | v0.5.2 | v0.5.3-rc1 |
|-----------------------|-----------------------|--------|------------|
| `xen_efi_launch`      | ✅                     | ❌      | ❌          |
| `xen_efi`             | ✅                     | ✅      | ✅          |
| `xen_mb2_launch`      | ✅                     | ❌      | ❌          |
| `linux_launch`        | ✅                     | ❌      | ❌          |
| `linux_legacy_launch` | ✅                     | ❌      | ❌          |
| `linux_alt_launch`    | ✅                     | ❌      | ❌          |
| `linux`               | ✅                     | ✅      | ✅          |

- `amd-drtm-test-image-4`: 109 passed.
- `v0.5.2`: 87 passed, 22 xfailed.
    - `xen_efi_launch` expected: the upstream Xen's MLE_JOIN has the GDT base as its limit
    - `xen_mb2_launch` expected: the upstream Xen's MLE_JOIN has the GDT base as its limit
    - `linux_launch` expected: the decompressor wipes boot_params the EFI stub placed there
    - `linux_legacy_launch` expected: no CONFIG_INTEL_IOMMU: the VT-d PMRs stay on and block the disk
    - `linux_alt_launch` expected: no CONFIG_INTEL_IOMMU: the VT-d PMRs stay on and block the disk
- `v0.5.3-rc1`: 87 passed, 22 xfailed.
    - `xen_efi_launch` expected: the upstream Xen's MLE_JOIN has the GDT base as its limit
    - `xen_mb2_launch` expected: the upstream Xen's MLE_JOIN has the GDT base as its limit
    - `linux_launch` expected: the decompressor wipes boot_params the EFI stub placed there
    - `linux_legacy_launch` expected: no CONFIG_INTEL_IOMMU: the VT-d PMRs stay on and block the disk
    - `linux_alt_launch` expected: no CONFIG_INTEL_IOMMU: the VT-d PMRs stay on and block the disk

<details>
<summary>Every test</summary>

| Test                                                                                              | amd-drtm-test-image-4 | v0.5.2  | v0.5.3-rc1 |
|---------------------------------------------------------------------------------------------------|-----------------------|---------|------------|
| `tests/test_console.py::test_a_dump_is_the_bytes_it_spells`                                       | passed                | passed  | passed     |
| `tests/test_console.py::test_the_newlines_a_long_dump_wraps_at_are_ignored`                       | passed                | passed  | passed     |
| `tests/test_console.py::test_a_hypervisor_line_spliced_into_a_dump_is_dropped`                    | passed                | passed  | passed     |
| `tests/test_console.py::test_a_hypervisor_line_spliced_into_the_middle_of_a_byte_is_dropped`      | passed                | passed  | passed     |
| `tests/test_console.py::test_a_dump_that_is_not_hex_still_raises`                                 | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_is_the_skls_events_then_xens`                           | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_header_declares_the_banks_in_its_order`                         | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[17-sha256]`                         | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[17-sha1]`                           | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[18-sha256]`                         | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_xen_log_replays_to_the_pcrs[18-sha1]`                           | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_has_the_kernels_tags`                                 | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[17-sha256]` | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[17-sha1]`   | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[18-sha256]` | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped[18-sha1]`   | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_the_zero_tail_of_the_log_region_is_not_an_event`                    | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_an_event_without_the_bank_leaves_that_banks_replay_alone`           | passed                | passed  | passed     |
| `tests/test_eventlog.py::test_an_empty_or_foreign_buffer_is_refused`                              | passed                | passed  | passed     |
| `tests/test_grubcfg.py::test_entries_keep_their_commands_in_order_without_the_noise`              | passed                | passed  | passed     |
| `tests/test_grubcfg.py::test_the_parameter_lands_on_the_kernel_line_alone`                        | passed                | passed  | passed     |
| `tests/test_grubcfg.py::test_an_entry_without_a_kernel_line_is_refused`                           | passed                | passed  | passed     |
| `tests/test_grubcfg.py::test_the_boot_partition_is_the_efi_system_partition`                      | passed                | passed  | passed     |
| `tests/test_grubcfg.py::test_a_disk_without_one_is_refused`                                       | passed                | passed  | passed     |
| `tests/test_grubcfg.py::test_the_menu_is_read_in_the_environment_given`                           | passed                | passed  | passed     |
| `tests/test_launch.py::test_launch_extends_the_drtm_pcrs[xen_efi_launch]`                         | passed                | passed  | passed     |
| `tests/test_launch.py::test_launch_extends_the_drtm_pcrs[xen_mb2_launch]`                         | passed                | passed  | passed     |
| `tests/test_launch.py::test_launch_extends_the_drtm_pcrs[linux_launch]`                           | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_launch_extends_the_drtm_pcrs[linux_legacy_launch]`                    | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_launch_extends_the_drtm_pcrs[linux_alt_launch]`                       | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_launch_brings_every_cpu_up[xen_efi_launch]`                           | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_launch_brings_every_cpu_up[xen_mb2_launch]`                           | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_launch_brings_every_cpu_up[linux_launch]`                             | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_launch_brings_every_cpu_up[linux_legacy_launch]`                      | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_launch_brings_every_cpu_up[linux_alt_launch]`                         | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_boot_shows_no_unexpected_errors[xen_efi_launch]`                      | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_boot_shows_no_unexpected_errors[xen_efi]`                             | passed                | passed  | passed     |
| `tests/test_launch.py::test_boot_shows_no_unexpected_errors[xen_mb2_launch]`                      | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_boot_shows_no_unexpected_errors[linux_launch]`                        | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_boot_shows_no_unexpected_errors[linux_legacy_launch]`                 | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_boot_shows_no_unexpected_errors[linux_alt_launch]`                    | passed                | xfailed | xfailed    |
| `tests/test_launch.py::test_boot_shows_no_unexpected_errors[linux]`                               | passed                | passed  | passed     |
| `tests/test_linux.py::test_launch_is_seen_by_linux`                                               | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_launch_brings_the_iommu_up`                                            | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_launch_log_declares_the_tpms_banks`                                    | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_legacy_launch_is_seen_by_linux`                                        | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_legacy_launch_brings_the_iommu_up`                                     | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_legacy_launch_log_declares_the_tpms_banks`                             | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_alt_launch_is_seen_by_linux`                                           | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_alt_launch_log_declares_the_tpms_banks`                                | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_the_command_line_is_measured_into_pcr_18_alone`                        | passed                | xfailed | xfailed    |
| `tests/test_linux.py::test_normal_boot_launches_nothing`                                          | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_workflow_gets_every_release_under_every_configuration`            | passed                | passed  | passed     |
| `tests/test_matrix.py::test_a_selection_of_releases_is_kept_in_the_order_given`                   | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env0-classic]`                | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env1-psp]`                    | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env2-sha256]`                 | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env3-psp-sha256]`             | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env4-sha384]`                 | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env5-psp]`                    | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env6-None]`                   | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env7-intel]`                  | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env8-intel-sha256]`           | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env9-intel-sha384]`           | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env10-None]`                  | passed                | passed  | passed     |
| `tests/test_matrix.py::test_the_environment_names_its_configuration[env11-classic]`               | passed                | passed  | passed     |
| `tests/test_matrix.py::test_a_cell_replaces_the_configuration_variables_and_the_local_image`      | passed                | passed  | passed     |
| `tests/test_menu.py::test_titles_come_out_in_menu_order_once_each`                                | passed                | passed  | passed     |
| `tests/test_menu.py::test_the_image_lists_every_entry_this_suite_knows`                           | passed                | passed  | passed     |
| `tests/test_qemu_binary.py::test_the_configured_binary_is_ours[amd]`                              | passed                | passed  | passed     |
| `tests/test_qemu_binary.py::test_the_configured_binary_is_ours[intel]`                            | passed                | passed  | passed     |
| `tests/test_qemu_binary.py::test_a_refused_option_is_reported`                                    | passed                | passed  | passed     |
| `tests/test_qemu_binary.py::test_a_warning_named_in_rejects_is_reported`                          | passed                | passed  | passed     |
| `tests/test_qemu_binary.py::test_a_missing_binary_is_reported`                                    | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_settings_hold_what_the_environment_said_when_read`                   | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_settings_carry_a_copy_of_the_environment`                            | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_settings_name_the_swtpm_programs_by_path`                            | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_settings_keep_a_missing_program_by_name`                             | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_a_vm_keeps_the_settings_it_was_made_with`                            | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_options_end_with_the_extra_arguments_given[extra0-expected0]`        | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_options_end_with_the_extra_arguments_given[extra1-expected1]`        | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_options_end_with_the_extra_arguments_given[None-expected2]`          | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_the_state_is_written_by_the_program_given`                           | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_the_program_runs_in_the_environment_given`                           | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_a_tpm_1_2_sits_behind_tis`                                           | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_a_tis_frontend_drops_the_hash_unless_told_not_to`                    | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_the_hash_drop_follows_the_environment[None-True]`                    | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_the_hash_drop_follows_the_environment[on-True]`                      | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_the_hash_drop_follows_the_environment[off-False]`                    | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_a_tpm_1_2_state_is_written_without_tpm2`                             | passed                | passed  | passed     |
| `tests/test_qemu_vm.py::test_the_running_cpus_are_the_ones_not_halted`                            | passed                | passed  | passed     |
| `tests/test_report.py::test_a_cell_says_what_the_boot_did`                                        | passed                | passed  | passed     |
| `tests/test_report.py::test_the_notes_say_what_was_expected`                                      | passed                | passed  | passed     |
| `tests/test_report.py::test_a_release_without_results_is_a_missing_column`                        | passed                | passed  | passed     |
| `tests/test_report.py::test_the_full_table_has_every_test_and_the_parser_ones_only_there`         | passed                | passed  | passed     |
| `tests/test_report.py::test_the_sections_and_columns_follow_the_matrix_order`                     | passed                | passed  | passed     |
| `tests/test_report.py::test_the_header_names_the_commit_the_run_and_the_tools`                    | passed                | passed  | passed     |
| `tests/test_report.py::test_a_badge_is_green_only_when_every_configuration_passed`                | passed                | passed  | passed     |
| `tests/test_report.py::test_a_missing_configuration_alone_is_red_too`                             | passed                | passed  | passed     |
| `tests/test_report.py::test_a_hand_made_session_gets_a_section_of_its_own`                        | passed                | passed  | passed     |
| `tests/test_report.py::test_the_sections_are_grouped_by_vendor_amd_first`                         | passed                | passed  | passed     |
| `tests/test_report.py::test_main_reads_a_tree_of_results_and_writes_the_page_and_badges`          | passed                | passed  | passed     |
| `tests/test_xen.py::test_efi_launch_is_seen_by_xen`                                               | passed                | passed  | passed     |
| `tests/test_xen.py::test_efi_launch_brings_the_iommu_up`                                          | passed                | passed  | passed     |
| `tests/test_xen.py::test_efi_launch_log_declares_the_tpms_banks`                                  | passed                | passed  | passed     |
| `tests/test_xen.py::test_efi_normal_boot_launches_nothing`                                        | passed                | passed  | passed     |
| `tests/test_xen.py::test_mb2_launch_is_seen_by_xen`                                               | passed                | passed  | passed     |
| `tests/test_xen.py::test_mb2_launch_brings_the_iommu_up`                                          | passed                | passed  | passed     |
| `tests/test_xen.py::test_mb2_launch_log_declares_the_tpms_banks`                                  | passed                | passed  | passed     |

</details>
