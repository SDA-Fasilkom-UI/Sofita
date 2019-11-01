<?php

defined('MOODLE_INTERNAL') || die();

class assign_submission_gradersda extends assign_submission_plugin {

    // Variable options
    public $statusoptions = array(
        'DEFAULT' => '-',
        'PENDING' => 'Pending.',
        'SUCCESS' => 'Successfully sent to grader.',
        'FAILED' => 'Failed to send submission, contact assistant.',
        'NOFILE' => 'No file submitted.',
        'FILEDISABLED' => 'File submissions is disabled, contact asisstant.'
    );
    public $timelimitoptions = array(1, 2, 3, 4, 5);
    public $memorylimitoptions = array(64, 128, 192, 256);

    /**
     * Get the name of the gradersda submission plugin
     * @return string
     */
    public function get_name() {
        return get_string('gradersda', 'assignsubmission_gradersda');
    }

    /**
     * Get the default setting for gradersda submission plugin
     *
     * @param MoodleQuickForm $mform The form to add elements to
     * @return void
     */
    public function get_settings(MoodleQuickForm $mform) {

        $defaulttimelimit = $this->get_config('timelimit');
        if (!$defaulttimelimit) {
            $defaulttimelimit = 1;
        }

        $defaultmemorylimit = $this->get_config('memorylimit');
        if (!$defaultmemorylimit) {
            $defaultmemorylimit = 1;
        }

        $defaultproblemname = $this->get_config('problemname');
        if (!$defaultproblemname) {
            $defaultproblemname = $this->statusoptions['DEFAULT'];
        }

        $name = get_string('problemname', 'assignsubmission_gradersda');
        $mform->addElement('text', 'assignsubmission_gradersda_problemname', $name);
        $mform->addHelpButton('assignsubmission_gradersda_problemname', 'problemname', 'assignsubmission_gradersda');
        $mform->setType('assignsubmission_gradersda_problemname', PARAM_TEXT);
        $mform->setDefault('assignsubmission_gradersda_problemname', $defaultproblemname);
        $mform->hideIf('assignsubmission_gradersda_problemname', 'assignsubmission_gradersda_enabled', 'notchecked');

        $name = get_string('timelimit', 'assignsubmission_gradersda');
        $mform->addElement('select', 'assignsubmission_gradersda_timelimit', $name, $this->timelimitoptions);
        $mform->addHelpButton('assignsubmission_gradersda_timelimit', 'timelimit', 'assignsubmission_gradersda');
        $mform->setDefault('assignsubmission_gradersda_timelimit', $defaulttimelimit);
        $mform->hideIf('assignsubmission_gradersda_timelimit', 'assignsubmission_gradersda_enabled', 'notchecked');

        $name = get_string('memorylimit', 'assignsubmission_gradersda');
        $mform->addElement('select', 'assignsubmission_gradersda_memorylimit', $name, $this->memorylimitoptions);
        $mform->addHelpButton('assignsubmission_gradersda_memorylimit', 'memorylimit', 'assignsubmission_gradersda');
        $mform->setDefault('assignsubmission_gradersda_memorylimit', $defaultmemorylimit);
        $mform->hideIf('assignsubmission_gradersda_memorylimit', 'assignsubmission_gradersda_enabled', 'notchecked');
    }

    /**
     * Save the settings for file submission plugin
     *
     * @param stdClass $data
     * @return bool
     */
    public function save_settings(stdClass $data) {
        $this->set_config('timelimit', $data->assignsubmission_gradersda_timelimit);
        $this->set_config('memorylimit', $data->assignsubmission_gradersda_memorylimit);
        $this->set_config('problemname', $data->assignsubmission_gradersda_problemname);
        return true;
    }

    /**
     * Display time limit, memory limit, and status
     *
     * @param stdClass $submission
     * @param bool $showviewlink Set this to true if the list of files is long
     * @return string
     */
    public function view_summary(stdClass $submission, & $showviewlink) {
        $filesubmission = $this->get_file_submission($submission->id);
        if ($filesubmission) {
            $status = $filesubmission->status;
        } else{
            $status = '-';
        }

        $timelimit = $this->timelimitoptions[$this->get_config('timelimit')];
        $memorylimit = $this->memorylimitoptions[$this->get_config('memorylimit')];

        return 'Time Limit: ' . $timelimit .
                's | Memory Limit: ' . $memorylimit .
                'MB | Status: ' . $status;
    }

    /**
     * The submission always not empty
     * @param stdClass $submission
     */
    public function is_empty(stdClass $submission) {
        return false;
    }

    /**
     * Get file submission information from the database
     *
     * @param int $submissionid
     * @return mixed
     */
    private function get_file_submission($submissionid) {
        global $DB;
        return $DB->get_record('assignsubmission_gradersda', array('submission'=>$submissionid));
    }

    /**
     * Save the assignment and create initial status to pending
     *
     * @param stdClass $submission
     * @param stdClass $data
     * @return bool
     */
    public function save(stdClass $submission, stdClass $data) {
        global $USER, $DB;

        $filesubmission = $this->get_file_submission($submission->id);
        if ($filesubmission) {
            $updatestatus = $DB->update_record('assignsubmission_gradersda', $filesubmission);
            return $updatestatus;
        } else {
            $filesubmission = new stdClass();
            $filesubmission->submission = $submission->id;
            $filesubmission->assignment = $this->assignment->get_instance()->id;
            $filesubmission->status = $this->statusoptions['PENDING'];
            $filesubmission->id = $DB->insert_record('assignsubmission_gradersda', $filesubmission);
            return $filesubmission->id > 0;
        }
    }

    /**
     * The assignment has been deleted - cleanup
     *
     * @return bool
     */
    public function delete_instance() {
        global $DB;

        // Will throw exception on failure.
        $DB->delete_records('assignsubmission_gradersda',
                            array('assignment'=>$this->assignment->get_instance()->id));

        return true;
    }

    /**
     * Update submission status
     *
     * @return bool
     */
    public function update_submission_status(stdClass $submission, $status) {
        global $DB;

        $filesubmission = $this->get_file_submission($submission->id);
        if ($filesubmission) {
            $filesubmission->status = $status;
            $updatestatus = $DB->update_record('assignsubmission_gradersda', $filesubmission);
            return $updatestatus;
        }
        return false;
    }

    /**
     * Send submission to grader
     * @param stdClass $submission the assign_submission record being submitted.
     * @return void
     */
    public function submit_for_grading($submission) {
        global $USER, $CFG;

        $ret = $this->assignment->get_submission_plugin_by_type('file');

        if ($ret->is_enabled()) {
            $fileareas = key($ret->get_file_areas());
            $fs = get_file_storage();
            $files = $fs->get_area_files($this->assignment->get_context()->id, 'assignsubmission_file', $fileareas, $submission->id, 'id', false);
            if (count($files) >= 1) {
                $file = array_values($files)[0];
                $content = $file->get_content();
                $contentencoded = base64_encode($content);

                $timelimit = $this->timelimitoptions[$this->get_config('timelimit')];
                $memorylimit = $this->memorylimitoptions[$this->get_config('memorylimit')];
                $problemname = $this->get_config('problemname');

                $url = $CFG->grader_url . "/api/grade";
                $token = $CFG->grader_token;

                $handle = curl_init($url);

                $data = [
                    'content' => $contentencoded,
                    'timelimit' => $timelimit,
                    'memorylimit' => $memorylimit,
                    'problemname' => $problemname,
                    'userid' => (int) $USER->id,
                    'attemptnumber' => (int) $submission->attemptnumber,
                    'assignmentid' => (int) $this->assignment->get_instance()->id
                ];
                $encodedData = json_encode($data);

                curl_setopt($handle, CURLOPT_POST, 1);
                curl_setopt($handle, CURLOPT_POSTFIELDS, $encodedData);
                curl_setopt($handle, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
                curl_setopt($handle, CURLOPT_HTTPHEADER, ['X_TOKEN: ' . $token]);
                curl_setopt($handle, CURLOPT_RETURNTRANSFER, true);

                $result = curl_exec($handle);

                // handle

            } else {
                $this->update_submission_status($submission, $this->statusoptions['NOFILE']);

                // handle no file
            }
        } else {
            $this->update_submission_status($submission, $this->statusoptions['FILEDISABLED']);

            // handle file disabled
        }
    }
}
