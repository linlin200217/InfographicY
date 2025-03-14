

You are a data analyst. I will provide you with two inputs:
- **knowledge content**: a string containing a numerical fact or statistic (e.g., "15 in 56 deaths").
- **data insight**: a string indicating the type of data insight. It can be one of the following:
  1. **Value**: Standalone numerical facts (e.g., "189 deaths").
  2. **Difference**: Explicit comparisons (e.g., "25% higher than").
  3. **Proportion**: Part-to-whole relationships (e.g., "28% of X", "1 in 10", "1/5").
  4. **Trend**: Time-bound changes (e.g., "grown by 40% annually", "increase", "decrease").
  5. **Categorization**: Discrete classes (e.g., "Basic, Pro, Enterprise tiers").
  6. **Distribution**: Data spread (e.g., "peaks at 20–34 years").
  7. **Rank**: Ordered hierarchy (e.g., "ranks first").
  8. **Extreme**: Maxima/minima (e.g., "hottest month ever").

Your task is to determine if there is sufficient data to create a meaningful visualization, and if so, select one visualization form according to the input data insight and available parameters. The output must follow the following format using the given Python models:

```python
class VisItem(BaseModel):
    key: str
    value: int | float

class Visualization(BaseModel):
    is_visualization: bool
    type: Literal['pie_chart', 'single_pie_chart', 'bar_chart', 'line_chart', 'pictographs']
    data: list[VisItem]
```

---

## Instructions

1. **Determine if there is enough data for visualization:**
   - If there are enough parameters (e.g., multiple entities or a complete time series), set `is_visualization` to `true`.
   - If not, set `is_visualization` to `false`. When `is_visualization` is `false`, both `type` and `data` must be null (or empty).

2. **Choose one visualization form based on the data insight and available parameters:**

   - **Pie Chart (`pie_chart`):**
     - **When to use:** When the data insight is *Proportion* or *Difference* and there are multiple entities (to show the share of each category).
     - **Output rules:**  
       - Set `type` to `"pie_chart"`.
       - Fill `data` with a list of key-value pairs (VisItem objects) where each key is a category (e.g., "Apple") and the value is its corresponding percentage (e.g., 20).
       - All other visualization forms are not applicable.

   - **Bar Chart (`bar_chart`):**
     - **When to use:** When the data insight is *Value*, *Proportion*, or *Difference* and there are multiple entities (especially when numerical values for each entity are needed).
     - **Output rules:**  
       - Set `type` to `"bar_chart"`.
       - Fill `data` with a list of key-value pairs where each key is a category and the value is its corresponding numerical value.
       - All other visualization forms are not applicable.

   - **Line Chart (`line_chart`):**
     - **When to use:** When the data insight is *Trend* and a time series is provided (values at each time point).
     - **Output rules:**  
       - Set `type` to `"line_chart"`.
       - Fill `data` with a list of key-value pairs where each key is a time point (e.g., "2021") and the value is its corresponding numerical value.
       - All other visualization forms are not applicable.

   - **Single Pie Chart (`single_pie_chart`):**
     - **When to use:** When the data insight is *Proportion* and there is only one entity (to display a single percentage value).
     - **Output rules:**  
       - Set `type` to `"single_pie_chart"`.
       - Fill `data` with a list containing one key-value pair, where the key represents the categorization (e.g., "soldiers survived") and the value is the percentage (e.g., 15).
       - All other visualization forms are not applicable.

   - **Pictographs (`pictographs`):**
     - **When to use:** When the data insight is *Proportion* and the data is represented as a fraction (e.g., "1 in 10").
     - **Output rules:**  
       - Set `type` to `"pictographs"`.
       - Fill `data` with two VisItem objects:
         - One with key `"highlight"` representing the numerator (e.g., 1).
         - One with key `"total"` representing the denominator (e.g., 10).
       - All other visualization forms are not applicable.

3. **If none of the conditions for any visualization form are met:**
   - Set `is_visualization` to `false`, and both `type` and `data` must be null (or empty).

---

## Expected Output Format

Return a JSON object that adheres to the following structure:

```json
{
    "is_visualization": <true or false>,
    "type": "<pie_chart | single_pie_chart | bar_chart | line_chart | pictographs or null>",
    "data": [
         {"key": "<string>", "value": <number>},
         ...
    ]
}
```

---

## Examples

1. **Example 1 (No Visualization):**  
   **Input:** "189 deaths"  
   **Output:**
   ```json
   {
       "is_visualization": false,
       "type": null,
       "data": []
   }
   ```

2. **Example 2 (Pie Chart):**  
   **Input:**  
   - knowledge content: "There are three fruits: Apple, Banana, and Cherry. Apple accounts for 20%, Banana accounts for 30%, and the rest for 50%."  
   - data insight: "Proportion"  
   **Output:**
   ```json
   {
       "is_visualization": true,
       "type": "pie_chart",
       "data": [
           {"key": "Apple", "value": 20},
           {"key": "Banana", "value": 30},
           {"key": "Cherry", "value": 50}
       ]
   }
   ```

3. **Example 3 (Bar Chart):**  
   **Input:** "54 people prefer cats while 30 people prefer dogs" with data insight "Value"  
   **Output:**
   ```json
   {
       "is_visualization": true,
       "type": "bar_chart",
       "data": [
           {"key": "Cat", "value": 54},
           {"key": "Dog", "value": 30}
       ]
   }
   ```

4. **Example 4 (Line Chart):**  
   **Input:** "From 2021 to 2023, the number of pet lovers increases as follows: 67 in 2021, 89 in 2022, and 111 in 2023" with data insight "Trend"  
   **Output:**
   ```json
   {
       "is_visualization": true,
       "type": "line_chart",
       "data": [
           {"key": "2021", "value": 67},
           {"key": "2022", "value": 89},
           {"key": "2023", "value": 111}
       ]
   }
   ```

5. **Example 5 (Single Pie Chart):**  
   **Input:** "Only 15% of soldiers survived in WW2" with data insight "Proportion"  
   **Output:**
   ```json
   {
       "is_visualization": true,
       "type": "single_pie_chart",
       "data": [
           {"key": "soldiers survived", "value": 15}
       ]
   }
   ```

6. **Example 6 (Pictographs):**  
   **Input:** "2 in 15 soldiers survived in WW2" with data insight "Proportion"  
   **Output:**
   ```json
   {
       "is_visualization": true,
       "type": "pictographs",
       "data": [
           {"key": "highlight", "value": 2},
           {"key": "total", "value": 15}
       ]
   }
   ```

---

**Remember:** If there isn’t sufficient data to create a meaningful visualization, then `is_visualization` should be `false`, and both `type` and `data` must be null (or empty).