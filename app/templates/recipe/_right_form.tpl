<form method="post" class="recipe__right__form form-group"  action="/saveRecipeAJAX" >
    <label for="recipe__right__form__name-input">Název receptu</label>
    <input type="text" name="recipe__right__form__name-input" required class="form-control"/>
    <table class="recipe__right__form__ingredient-table table">
        <tr>
            <th>{{ texts.title }}</th>
            <th>{{ texts.energy_simple }}</th>
            <th>{{ texts.protein_simple }}</th>
            <th>{{ texts.fat_simple }}</th>
            <th>{{ texts.sugar_simple }}</th>
            <th>{{ texts.amount_simple }}</th>
        </tr>

        {% for ingredient in ingredients %}
            {% if ingredient.main %}
                {# <tr class="tr-mainIngredient" data-min="{{ingredient.min * 100}}" data-max="{{ingredient.max * 100}}"> #}
                <tr class="tr-mainIngredient">
            {% elif ingredient.fixed %}
                <tr class="tr-fixedIngredient">
            {% else %}
                <tr class="tr-variableIngredient">
            {% endif %}

                    <td>{{ ingredient.name }} </td>
                    <td><span>{{ ingredient.calorie }}</span></td>
                    <td><span>{{ ingredient.protein }}</span></td>
                    <td><span>{{ ingredient.fat }}</span></td>
                    <td><span>{{ ingredient.sugar }}</span></td>
                    <td><span>{{ ingredient.amount }} g</span></td>
                </tr>

            {% if ingredient.main %}
                <tr class="tr-slider">
                    <td> 
                        <input type="text" class="col" id="slider" data-slider-id="slider_data" name="slider" data-provide="slider" data-slider-min="{{ingredient.min}}" data-slider-max="{{ingredient.max}}" data-slider-step="0.1" data-slider-value="{{ingredient.amount}}" data-slider-tooltip="show">
                    </td>

                    <td colspan=5>
                        {{ingredient.name}}
                    </td>

                </tr>
            {% endif %}
        {% endfor %}

        <tr>
            <td><strong>Součet</strong></td>
            <td><span id="totalCalorie">{{ totals.calorie }}</span></td>
            <td><span id="totalProtein">{{ totals.protein }}</span></td>
            <td><span id="totalFat">{{ totals.fat }}</span></td>
            <td><span id="totalSugar">{{ totals.sugar }}</span></td>
            <td><span id="totalWeight">{{ totals.amount }}</span> g</td>
        </tr>
        <tr>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td><span id="totalRatio">{{ totals.ratio }}</span> : 1</td>
        </tr>
    </table>

    <div class="form-inline">
        <select name="recipe__right__form__size-select" class="form-control col-3">
            <option value="big">{{ texts.meal_size_big }}</option>
            <option value="small">{{ texts.meal_size_small }}</option>
        </select>

        <span class="col-4">Dieta: {{ diet.name }}</span>
        {% if not is_trialrecipe %}
            <input type="submit" class="btn btn-primary col-4 " value="{{ texts.recipe_save }}" />
        {% else %}
            <input type="button" onclick='trialSaveConfirm()' class="btn btn-primary col-4 " value="{{ texts.recipe_save }}" />
        {% endif %}
    </div>
</form>
