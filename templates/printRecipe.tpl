{% extends "base.tpl" %}
{% block title %}
    Vytisknout recept - {{ recipe.name }}
{% endblock %}

{% block style %}
    <style type="text/css" media="screen">
		.totals {
			background-color: lightgrey;
		}      

		@media print {
			body {-webkit-print-color-adjust: exact;}
			.totals {
				background-color: lightgrey;
			}
		}
    </style>
{% endblock %}

{% block script %}
	
{% endblock %}

{% block content %}
    <div class="container">
        <div class="col-12 d-print-flex">

            <span class="data__table d-print-table"><h2>{{ recipe.name }}</h2></span>
            <span>
                {% if recipe.size == "small" %}
                    <h5>Malé jídlo ({{ diet.small_size }}%)</h5>
                {% elif recipe.size == "big" %}
                    <h5>Velké jídlo ({{ diet.big_size }}%)</h5> 
                {% endif %}
            </span>            
            <table id="ingredients" class="table">
                <tr>
                    <th><strong>Název</strong></th>
                    <th><strong>Kalorie</strong></th>
                    <th><strong>Bílkovina</strong></th>
                    <th><strong>Tuk</strong></th>
                    <th><strong>Sacharidy</strong></th>
                    <th><strong>Množství</strong></th>
                    <th></th>
                </tr>

                {% for ingredient in ingredients: %}
                    <tr>
                        <td><strong>{{ ingredient.name }}</strong></td>
                        <td>{{ (ingredient.calorie / 100 * ingredient.amount)|round(2,'common') }} kcal</td>
                        <td>{{ (ingredient.protein / 100 * ingredient.amount)|round(2,'common') }} g</td>
                        <td>{{ (ingredient.fat / 100 * ingredient.amount)|round(2,'common') }} g</td>
                        <td>{{ (ingredient.sugar / 100 * ingredient.amount)|round(2,'common') }} g</td>
                        <td>{{ ingredient.amount|round(2,'common') }} g</td>
                        <td></td>
                    </tr>
                {% endfor %}

                <tr class="totals">
                    <td><strong>Celkem</strong></td>
                    <td>{{ totals.calorie }} kcal</td>
                    <td>{{ totals.protein }} g</td>
                    <td>{{ totals.fat }} g</td>
                    <td>{{ totals.sugar }} g</td>
                    <td>{{ totals.amount|round(2,'common') }} g</td>
                    <td>{{ totals.eq }} : 1</td>
                </tr>
            </table>
            </div>
        </div>
    </div>
{% endblock %}

