/* ============================================================
   CS 3431 - Database Systems I
   Worcester Polytechnic Institute (WPI)

   Sakire Arslan Ay
   All rights reserved.
   This code is provided for educational purposes only and may not be used for commercial applications.
   Note: This is starter code provided to students.
   Modify as instructed in the assignment.
 ============================================================*/

package yelpapp.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import yelpapp.model.Business;
import yelpapp.model.YelpRepository;

import java.util.*;
import java.util.List;


@RestController
@RequestMapping("/api")
@CrossOrigin(origins = "http://localhost:3000")
public class YelpController {

    private final YelpRepository yelpRepository;

    @Autowired
    public YelpController(YelpRepository yelpRepository) {
        this.yelpRepository = yelpRepository;
    }

    /*
    http://localhost:3000
    /api/states

    Example response:[
    {
        "states": [
            "AZ", ...
        ]
    }
]
    */
    @GetMapping("/states")
    public ResponseEntity<?> getStates() {
        List<String> states;
        try {
            states = yelpRepository.getStateData();
        } catch (Exception ex) {
            throw new RuntimeException("Could not get the states...", ex);
        }
        return ResponseEntity.ok(List.of(Map.of("states", states)));
    }

    /*
     http://localhost:3000
     /api/filters?state=AZ&city=Phoenix
     Example response:
     [
    {"categories": [
            "Acai Bowls", ... ],
     "attributes": [
            "AcceptsInsurance", ... ]
             } ]
     */
    @GetMapping("/filters")
    public ResponseEntity<?> getFilters(@RequestParam String state, @RequestParam String city) {
        List<String> categories;
        List<String> attributes;
        try {
            categories = yelpRepository.getCategories(state, city);
        } catch (Exception ex) {
            throw new RuntimeException("Could not get the categories for the state and city...", ex);
        }
        try {
            attributes = yelpRepository.getAttributes(state, city);
        } catch (Exception ex) {
            throw new RuntimeException("Could not get the attributes for the state and city...", ex);
        }
        return ResponseEntity.ok(List.of(Map.of("categories", categories, "attributes", attributes)));
    }

    /*
    http://localhost:3000
    /api/businesses
    {
    "state": "NC",
    "city": "Charlotte"
    "categories": ["Restaurants", "Food"]
    "attributes": ["breakfast", "brunch"]
    }
  */
    @RequestMapping(value = "/businesses", method = {RequestMethod.GET, RequestMethod.POST})
    public ResponseEntity<?> getBusinesses(@RequestBody Map<String, Object> body) {
        List<Business> businesses;
        List<String> categories;
        List<String> attributes;
        String state;
        String city;
        String wifi = (String) body.get("wifi");
        String priceRange = (String) body.get("priceRange");

        // Validate and parse required fields from the request body
        try {
            state = body.get("state").toString();
            city = body.get("city").toString();
        } catch (Exception ex) {
            return ResponseEntity.badRequest().body(Map.of(
                    "error", "Required fields: state, city",
                    "details", ex.getMessage()
            )); //filter on both state AND CITY
        }
        // get the optional fields if they exist
        categories = (List<String>) body.get("categories");
        attributes = (List<String>) body.get("attributes");

        try {
            businesses = yelpRepository.queryBusinesses(state, city, categories, attributes, wifi, priceRange);
        } catch (Exception ex) {
            throw new RuntimeException("Search failed...", ex);
        }
        return ResponseEntity.ok(List.of(Map.of("businesses", businesses)));
    }

    /*
    http://localhost:3000
    /api/businesses/{bid}
    Example response:
    [
    {
        "business": {
            "business_id": "dQj5DLZjeDK3KFysh1SYOQ",
            "city": "Pittsburgh",
            "state": "PA",
            "zipcode": "15224",
            "latitude": 40.4656937,
            "longitude": -79.9493238,
            "star_rating": 4.5,
            "rank": 0,
            "distance": 0.0,
            "business_name": "Apteka",
            "num_tips": 7,
            "street_address": "4606 Penn Ave"
        }
    }
]
    */
    @GetMapping("/businesses/{bid}")
    public ResponseEntity<?> getBusinessDetails(@PathVariable String bid) {
        Business businessDetails;
        List<String> categories;
        List<Map<String, String>> attributes;
        Map<String, String> todaySchedule;
        List<Business> similarBusinesses;

        try {
            businessDetails = yelpRepository.getBusinessDetails(bid);
            categories = yelpRepository.getBusinessCategories(bid);
            attributes = yelpRepository.getBusinessAttributes(bid);
            todaySchedule = yelpRepository.getTodaySchedule(bid);
            similarBusinesses = yelpRepository.getSimilarBusinesses(bid);
        } catch (Exception ex) {
            throw new RuntimeException("Could not find the business for the given business id...", ex);
        }
        Map<String, Object> result = new HashMap<>();
        result.put("business", businessDetails);
        result.put("categories", categories);
        result.put("attributes", attributes);
        result.put("today_schedule", todaySchedule);
        result.put("similar_businesses", similarBusinesses);
        return ResponseEntity.ok(List.of(result));
    }

    /*
     http://localhost:3000
     /api/cities?state=AZ
     Example response:
     [
    {"cities": [
            "city name", ] } ]
     */
    @GetMapping("/cities")
    public ResponseEntity<?> getCities(@RequestParam String state) {
        List<String> cities;
        try {
            cities = yelpRepository.queryCities(state);
        } catch (Exception ex) {
            throw new RuntimeException("Could not get the cities for the state...", ex);
        }
        return ResponseEntity.ok(List.of(Map.of("cities", cities)));
    }

    @GetMapping("/wifi-pricerange")
    public ResponseEntity<?> getWiFiAndPriceRange(@RequestParam String state, @RequestParam String city) {
        Map<String, List<String>> result;
        try {
            result = yelpRepository.queryWiFiPriceRange(state, city);
        } catch (Exception ex) {
            throw new RuntimeException("Could not get the cities for the state...", ex);
        }
        return ResponseEntity.ok(List.of(result));
    }

}
