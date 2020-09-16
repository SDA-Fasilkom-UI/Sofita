<?php

defined('MOODLE_INTERNAL') || die();

class assign_submission_gradersda extends assign_submission_plugin {

    // Variable options
    public $statusoptions = array(
        'DEFAULT' => '-',
        'DRAFT' => 'Draft',
        'SUCCESS' => 'Successfully sent to grader',
        'FAILED' => 'Failed to send submission, retry later and contact assistant',
        'NOFILE' => 'Only one file allowed',
        'FILEDISABLED' => 'File submission is disabled, contact assistant'
    );
    public $timelimitoptions = array(1, 2, 3, 4, 5);
    public $memorylimitoptions = array(64, 128, 192, 256, 512);
    public $summary = "";

    public $maxretry = 5;
    public $retrysleepsecond = 2;

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
        global $CFG;

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
            $defaultproblemname = "-";
        }

        $name = get_string('problemname', 'assignsubmission_gradersda');
        $options = array(
            'ajax' => 'assignsubmission_gradersda/autocomplete_problems',
            'data-grader_url' => $CFG->grader_url,
        );
        $mform->addElement('autocomplete', 'assignsubmission_gradersda_problemname', $name, array(), $options);
        $mform->addHelpButton('assignsubmission_gradersda_problemname', 'problemname', 'assignsubmission_gradersda');
        $mform->setDefault('assignsubmission_gradersda_problemname', $defaultproblemname);

        $name = get_string('timelimit', 'assignsubmission_gradersda');
        $mform->addElement('select', 'assignsubmission_gradersda_timelimit', $name, $this->timelimitoptions);
        $mform->addHelpButton('assignsubmission_gradersda_timelimit', 'timelimit', 'assignsubmission_gradersda');
        $mform->setDefault('assignsubmission_gradersda_timelimit', $defaulttimelimit);

        $name = get_string('memorylimit', 'assignsubmission_gradersda');
        $mform->addElement('select', 'assignsubmission_gradersda_memorylimit', $name, $this->memorylimitoptions);
        $mform->addHelpButton('assignsubmission_gradersda_memorylimit', 'memorylimit', 'assignsubmission_gradersda');
        $mform->setDefault('assignsubmission_gradersda_memorylimit', $defaultmemorylimit);
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
     * @param bool $showviewlink Do not touch this
     * @return string
     */
    public function view_summary(stdClass $submission, & $showviewlink) {

        // Avoid calling multiple summary
        if (strlen($this->summary) === 0) {
            $timelimit = $this->timelimitoptions[$this->get_config('timelimit')];
            $memorylimit = $this->memorylimitoptions[$this->get_config('memorylimit')];

            $activity_id = $this->get_activity_id();

            $this->summary = 'Time Limit: ' . $timelimit .
                    's | Memory Limit: ' . $memorylimit .
                    'MB<br>Assignment ID: ' . $this->assignment->get_instance()->id .
                    ' | Course ID: ' . $this->assignment->get_instance()->course .
                    ' | Activity ID: ' . $activity_id .
                    ' | User ID: ' . $submission->userid . "<br>";
        }

        $filesubmission = $this->get_file_submission($submission->id);

        if ($filesubmission) {
            $status = $filesubmission->status;
        } else{
            $status = '-';
        }

        return $this->summary . "Status: " . $status;
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
     * Get user information from the database
     *
     * @param int $userid
     * @return mixed
     */
    private function get_user($userid) {
        global $DB;
        return $DB->get_record('user', array('id'=>$userid));
    }

    /**
     * Save the assignment and create initial status to draft
     *
     * @param stdClass $submission
     * @param stdClass $data
     * @return bool
     */
    public function save(stdClass $submission, stdClass $data) {
        global $DB;

        $filesubmission = $this->get_file_submission($submission->id);
        if ($filesubmission) {
            $updatestatus = $DB->update_record('assignsubmission_gradersda', $filesubmission);
            return $updatestatus;
        } else {
            $filesubmission = new stdClass();
            $filesubmission->submission = $submission->id;
            $filesubmission->assignment = $this->assignment->get_instance()->id;
            $filesubmission->status = $this->statusoptions['DRAFT'];
            $filesubmission->id = $DB->insert_record('assignsubmission_gradersda', $filesubmission);
            return $filesubmission->id > 0;
        }
    }

    /**
     * Get activity ID
     *
     */
    public function get_activity_id() {
        global $PAGE;
        return $PAGE->cm->id;
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
     * @param stdClass $submission
     * @param string $status
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
     * Check grader if alive or not
     * @return void
     */
    public function check_grader() {
        global $CFG;

        $url = $CFG->grader_url . "/api/check/";
        $handle = curl_init($url);
        curl_setopt($handle, CURLOPT_RETURNTRANSFER, true);

        $result = curl_exec($handle);
        $statuscode = curl_getinfo($handle, CURLINFO_HTTP_CODE);

        $check = true;
        if (!$result || $statuscode !== 200) {
            $check = false;
        }

        curl_close($handle);
        return $check;
    }

    /**
     * Send submission to grader
     * @param stdClass $submission the assign_submission record being submitted.
     * @param action $action the requested action
     * @param data $data data to be submitted
     * @return bool
     */
    public function send_to_grader($submission, $action, $data) {
        global $CFG;

        $url = $CFG->grader_url . "/api/" . $action . "/";
        $token = $CFG->grader_token;

        $cntretry = 0;
        $sent = false;
        while (!$sent && $cntretry < $this->maxretry) {
            $handle = curl_init($url);
            $encodeddata = json_encode($data);

            curl_setopt($handle, CURLOPT_POST, 1);
            curl_setopt($handle, CURLOPT_POSTFIELDS, $encodeddata);
            curl_setopt($handle, CURLOPT_HTTPHEADER, ['Content-Type: application/json', 'X-TOKEN: ' . $token]);
            curl_setopt($handle, CURLOPT_RETURNTRANSFER, true);

            $result = curl_exec($handle);
            $statuscode = curl_getinfo($handle, CURLINFO_HTTP_CODE);

            $sent = true;
            if (!$result || $statuscode !== 200) {
                $sent = false;
                sleep($this->retrysleepsecond);
            }
            curl_close($handle);

            $cntretry = $cntretry + 1;
        }

        return $sent;
    }

    /**
     * Precheck submission
     * @param stdClass $submission the assign_submission record being submitted.
     * @return bool|string 'true' if OK to proceed with submission, otherwise a
     *                        a message to display to the user
     */
    public function precheck_submission($submission) {
        $ret = $this->assignment->get_submission_plugin_by_type('file');

        if (!$ret->is_enabled()) {
            return $this->statusoptions['FILEDISABLED'];
        }

        $fileareas = key($ret->get_file_areas());
        $fs = get_file_storage();
        $files = $fs->get_area_files($this->assignment->get_context()->id, 'assignsubmission_file', $fileareas, $submission->id, 'id', false);

        if (count($files) < 1 || count($files) > 1) {
            return $this->statusoptions['NOFILE'];
        }

        $sent = $this->check_grader($submission, $data);
        if (!$sent) {
            $this->update_submission_status($submission, $this->statusoptions['FAILED']);
            return $this->statusoptions['FAILED'];
        }

        return true;
    }


    /**
     * Post process submission
     * @param stdClass $submission the assign_submission record being submitted.
     * @return void
     */
    public function submit_for_grading($submission) {
        $user = $this->get_user($submission->userid);
        $ret = $this->assignment->get_submission_plugin_by_type('file');

        $data = [
            'userid' => (int) $user->id,
            'attemptnumber' => (int) $submission->attemptnumber + 1,
            'assignmentid' => (int) $this->assignment->get_instance()->id,
            'courseid' => (int) $this->assignment->get_instance()->course,
            'activityid' => (int) $this->get_activity_id()
        ];

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

                $data['content'] = $contentencoded;
                $data['timelimit'] = $timelimit;
                $data['memorylimit'] = $memorylimit;
                $data['problemname'] = $problemname;
                $data['idnumber'] = $user->idnumber;
                $data['filename'] = $file->get_filename();
                $data['duedate'] = $this->assignment->get_instance()->duedate;
                $data['cutoffdate'] = $this->assignment->get_instance()->cutoffdate;
                $data['timemodified'] = $submission->timemodified;

                $this->update_submission_status($submission, $this->statusoptions['SUCCESS']);

                $sent = $this->send_to_grader($submission, 'grade', $data);
                if (!$sent) {
                    $this->update_submission_status($submission, $this->statusoptions['FAILED']);
                }

            } else {
                $this->update_submission_status($submission, $this->statusoptions['NOFILE']);
                $this->send_to_grader($submission, 'skip', $data);
            }
        } else {
            $this->update_submission_status($submission, $this->statusoptions['FILEDISABLED']);
            $this->send_to_grader($submission, 'skip', $data);
        }
    }
}
