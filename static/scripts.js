<script>
$(document).ready(function() {
    $('#integerForm').formValidation({
        framework: 'bootstrap',
        icon: {
            valid: 'glyphicon glyphicon-ok',
            invalid: 'glyphicon glyphicon-remove',
            validating: 'glyphicon glyphicon-refresh'
        },
        fields: {
            number: {
                validators: {
                    integer: {
                        message: 'The value is not an integer'
                    }
                }
            }
        }
    }
    );
</script>