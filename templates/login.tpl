{% extends "base.tpl" %}
{% block title %}
    Přihlašování
{% endblock %}

{% block style %}
    
{% endblock %}

{% block script %}

{% endblock %}

{% block content %}
    {% include('navbar_login.tpl') %}
    <div class="container">
    	<div class="col-12">
    		<form id="loginForm" action="/login" method="post" class="form-group form-control" >
    	        <label for="username">Přihlašovací email</label>
    	        <input name="username" type="text" required class="form-control" />

    	        <label for="password">Heslo</label>
    	        <input name="password" type="password" required class="form-control" />
    	        <span id=wrongLogin></span>

    	        <input name="loginButton" value="Přihlásit" type="submit" class="btn btn-primary col-sm-3" />
            	<a class="col-sm-2" href="/register">Registrovat</a>
    	    </form>
    	</div>
    </div>
{% endblock %}

