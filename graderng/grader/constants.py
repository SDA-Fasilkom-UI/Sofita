DIRECTORY_NOT_FOUND_OR_INVALID_ERROR_TEXT = "Directory not found"
DIRECTORY_NOT_FOUND_OR_INVALID_ERROR = \
    """
    <p><b> Error | Attempt Grade: 0 </b></p>
    <p> Problem directory is not found or invalid, contact assistant </p>
    """

COMPILATION_ERROR = \
    """
    {% load grader_extras %}

    <p><b> Compile Error | Attempt Grade: 0 </b></p>
    <p><b> First 20 Lines Compilation Output: </b></p>
    <table style="border: 1px solid black">
        <tr><td>
            <pre>{{ error }}</pre>
        </td></tr>
    </table>
    """

VERDICT_FEEDBACK = \
    """
    {% load grader_extras %}

    <p><b> Attempt Grade: {{ grade|floatformat:2 }}</b></p>
    <p><b> Summary: </b></p>
    <table style="border-collapse: collapse">
        {% with verdict_length=verdict|length %}
        {% with half1_verdict_length=verdict_length|div:2 %}
        {% with half2_verdict_length=verdict_length|subtract:half1_verdict_length %}
        {% with half=half2_verdict_length|to_range %}

        {% for i in half %}
            <tr>
                <td style="border: 1px solid black; text-align=left; padding: 4px;"><tt>
                    {{ i|add:1 }}: {{ verdict|index:i|index:0 }} ({{ verdict|index:i|index:1|floatformat:3 }})
                </tt></td>
                {% with next_i=half2_verdict_length|add:i %}
                {% if next_i < verdict_length %}
                    <td style="border: 1px solid black; text-align=left; padding: 4px;"><tt>
                        {{ next_i|add:1 }}:
                            {{ verdict|index:next_i|index:0 }} ({{ verdict|index:next_i|index:1|floatformat:3 }})
                    </tt></td>
                {% endif %}
                {% endwith %}
            </tr>
        {% endfor %}

        {% endwith %}
        {% endwith %}
        {% endwith %}
        {% endwith %}
    </table>
    <br>
    <p><tt>
        AC : Accepted <br>
        WA : Wrong Answer<br>
        RTE: Runtime Error<br>
        TLE: Time Limit Exceeded<br>
        XX : Unknown Error
    </tt></p>
    """

SUBMISSION_SKIPPED = "<b> Skipped </b>"

SUBMISSION_NOT_FOUND = \
    """
    <p><b> Error | Attempt Grade: 0 </b></p>
    <p> Submission is not found on grader, contact assistant </p>
    """
