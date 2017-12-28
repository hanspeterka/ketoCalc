<!DOCTYPE html>
<html>
<head>
	<meta charset="utf-8">
	<meta http-equiv="X-UA-Compatible" content="IE=edge">
	<title>Přihlašování</title>
	% include('bootstrap.tpl')
	% include('styleBody.tpl')
	<script type="text/javascript">
        $(document).on("submit", "#loginForm", function(e) {
        // $("#loginForm").on("submit", function(e) {
            $.ajax({
                type: 'POST',
                url: '/login',
                data: $(this).serialize(),
                success: function(response) {
                    if (!response){
                    	// console.log("");
                    	$("#wrongLogin").empty();
						$("#wrongLogin").append("<small class='form-text'>Chybné přihlašovací údaje</small>");
                    } else {
                    	window.location.replace("/user");
                	}
                },
                error: function(error) {
                    console.log(error);
                }

            });
            e.preventDefault();
        });
    </script>
</head>
<body>
    % include ('navbar_login.tpl')
	<div class="col-sm-6">
		<form id="loginForm" action="/login" method="post" class="form-group" >
	        <label for="username">Přihlašovací email</label>
	        <input name="username" type="text" class="form-control" />

	        <label for="password">Heslo</label>
	        <input name="password" type="password" class="form-control" />
	        <span id=wrongLogin></span>

	        <input name="loginButton" value="Přihlásit" type="submit" class="btn btn-primary col-sm-3" />
        	<a class="col-sm-2" href="/register">Registrovat</a>
	    </form>
	    
	</div>
</body>
</html>