/* ============================================================
   CS 3431 - Database Systems I
   Worcester Polytechnic Institute (WPI)

   Sakire Arslan Ay
   All rights reserved.
   This code is provided for educational purposes only and may not be used for commercial applications.
   Note: This is starter code provided to students.
   Modify as instructed in the assignment.
 ============================================================*/

package yelpapp.model;

import java.sql.*;
import java.util.ArrayList;
import java.util.List;

import io.github.cdimascio.dotenv.Dotenv;
import org.springframework.stereotype.Repository;

import java.util.Map;
import java.util.HashMap;
import java.util.logging.Logger;

@Repository
public class YelpRepository {

    private static final Dotenv dotenv = Dotenv.load();
    private static final String JDBC_URL = dotenv.get("JDBC_URL");
    private static final String JDBC_USER = dotenv.get("JDBC_USER");
    private static final String JDBC_PASS = dotenv.get("JDBC_PASS");

    private static final Logger logger = Logger.getLogger(YelpRepository.class.getName());

    private Connection connection;

    public List<String> getStateData() {
        List<String> states = new ArrayList<>();
        logger.info("getStates called in initialize. ");
        String stateQuery = """
                    SELECT DISTINCT state
                    FROM business
                    ORDER BY state
                """;
        try {
            connection = DriverManager.getConnection(JDBC_URL,JDBC_USER, JDBC_PASS );
        } catch (SQLException ex) {
            ex.printStackTrace();
        }

        try (PreparedStatement ps = connection.prepareStatement(stateQuery)){
            logger.info("Executing query: " + stateQuery);
            ResultSet rs = ps.executeQuery();
            while (rs.next()) {
                states.add(rs.getString("state"));
            }
        } catch (SQLException ex) {
            logger.severe("Error executing query: " + ex.getMessage());
            ex.printStackTrace();
        }

        try {
            connection.close();
        } catch (SQLException ex) {
            ex.printStackTrace();
        }
        return states;
    }

    public List<String> getCategories(String state, String city) {
        List<String> categories = new ArrayList<>();
        logger.info("getCategories called in initialize");
        if (state == null) {
            return categories;
        }
        String categoryQuery = """
            SELECT DISTINCT bc.categoryname
            FROM business_category bc
            JOIN business ON business.businessid = bc.businessid
            WHERE business.state = ? AND business.city = ?
            ORDER BY bc.categoryname
            """;
        try {
            connection = DriverManager.getConnection(JDBC_URL,JDBC_USER, JDBC_PASS );
        } catch (SQLException ex) {
            ex.printStackTrace();
        }

        try (PreparedStatement ps = connection.prepareStatement(categoryQuery)){
            logger.info("Executing query: " + categoryQuery);
            ps.setString(1, state); //fills the ? parameter
            ps.setString(2,city);
            ResultSet rs = ps.executeQuery();
            while (rs.next()) {
                categories.add(rs.getString("categoryname"));
            }
        } catch (SQLException ex) {
            logger.severe("Error executing query: " + ex.getMessage());
            ex.printStackTrace();
        }
        try {
            connection.close();
        } catch (SQLException e) {
            e.printStackTrace();
        }

        return categories;
    }

    public List<String> getAttributes(String state, String city) {
        List<String> attributes = new ArrayList<>();
        logger.info("getCategories called in initialize");
        if (state == null) {
            return attributes;
        }
        String attributeQuery = """
            SELECT DISTINCT BA.attributename
            FROM business
            INNER JOIN business_attribute BA on BA.businessid = business.businessid
            WHERE business.state = ? AND business.city = ? AND BA.value = 'True'
            ORDER BY BA.attributename
            """;
        try {
            connection = DriverManager.getConnection(JDBC_URL,JDBC_USER, JDBC_PASS );
        } catch (SQLException ex) {
            ex.printStackTrace();
        }

        try (PreparedStatement ps = connection.prepareStatement(attributeQuery)){
            logger.info("Executing query: " + attributeQuery);
            ps.setString(1, state); //fills the ? parameter
            ps.setString(2,city);
            ResultSet rs = ps.executeQuery();
            while (rs.next()) {
                attributes.add(rs.getString("attributename"));
            }
        } catch (SQLException ex) {
            logger.severe("Error executing query: " + ex.getMessage());
            ex.printStackTrace();
        }
        try {
            connection.close();
        } catch (SQLException e) {
            e.printStackTrace();
        }

        return attributes;
    }

    public List<Business> queryBusinesses(String state, String city, List<String> categories, List<String> attributes, String wifi, String priceRange) {
        List<Business> res = new ArrayList<>();
        logger.info("queryBusinesses is called.");

        String businessQuery = """ 
    SELECT businessid AS business_id, name AS business_name, streetaddress AS street_address,
    city, state, zip AS zipcode, latitude, longitude, stars AS star_rating, num_tips
    FROM business
    WHERE state = ? AND city = ?
    """;
        for (String cat: categories) {
            businessQuery += """
    AND EXISTS (
    SELECT * FROM business_category bc
    WHERE bc.businessid = business.businessid
    AND bc.categoryname = ?
    )
""";
        }
        for (String atr: attributes) {
            businessQuery += """
    AND EXISTS (
       SELECT *
       FROM business_attribute BA
       WHERE BA.attributename = ? AND BA.businessid = business.businessid
       AND BA.value = 'True'
    )
""";
        }
        if (wifi != null) {
            businessQuery += """
    AND EXISTS (
        SELECT *
        FROM business_attribute BA
        WHERE BA.businessid = business.businessid
        AND BA.attributename = 'WiFi'
        AND BA.value = ?
    )
""";
        }
        if (priceRange != null) {
            businessQuery += """
    AND EXISTS (
        SELECT *
        FROM business_attribute BA
        WHERE BA.businessid = business.businessid
        AND BA.attributename = 'RestaurantsPriceRange2'
        AND BA.value = ?
    )
""";
        }
        businessQuery += """
        ORDER BY business.name
    """;

        try {
            connection = DriverManager.getConnection(JDBC_URL, JDBC_USER, JDBC_PASS);
        } catch (SQLException ex) {
            ex.printStackTrace();
        }

        try (PreparedStatement ps = connection.prepareStatement(businessQuery)) {
            ps.setString(1, state);
            ps.setString(2, city);
            int count = 3;
            for (String cat: categories) {
                ps.setString(count, cat);
                count++;
            }
            for (String atr: attributes) {
                ps.setString(count, atr);
                count++;
            }
            if (wifi != null) {
                ps.setString(count, wifi);
                count++;
            }
            if (priceRange != null) {
                ps.setString(count, priceRange);
                count++;
            }
            try (ResultSet rs = ps.executeQuery()) {
                while (rs.next()) {
                    res.add(new Business(
                            rs.getString("business_id"),
                            rs.getString("business_name"),
                            rs.getString("street_address"),
                            rs.getString("city"),
                            rs.getString("state"),
                            rs.getString("zipcode"),
                            rs.getDouble("latitude"),
                            rs.getDouble("longitude"),
                            rs.getFloat("star_rating"),
                            rs.getInt("num_tips"),
                            0,
                            0.0
                    ));
                }
            }
        } catch (SQLException ex) {
            logger.severe("Business search failed! " + ex.getMessage());
        }
        try {
            connection.close();
        } catch (SQLException e) {
            e.printStackTrace();
        }
        return res;
    }

    public Business getBusinessDetails(String business_id) {
        Business res = null;

        String businessQuery = """
        SELECT businessid AS business_id, name AS business_name, streetaddress AS street_address,
        city, state, zip AS zipcode, latitude, longitude, stars AS star_rating, num_tips
          FROM business
         WHERE businessid  = ?
        """;

        try {
            connection = DriverManager.getConnection(JDBC_URL, JDBC_USER, JDBC_PASS);
        } catch (SQLException ex) {
            ex.printStackTrace();
        }

        try (PreparedStatement ps = connection.prepareStatement(businessQuery)) {
            ps.setString(1, business_id);

            try (ResultSet rs = ps.executeQuery()) {
                while (rs.next()) {
                    res = new Business(
                            rs.getString("business_id"),
                            rs.getString("business_name"),
                            rs.getString("street_address"),
                            rs.getString("city"),
                            rs.getString("state"),
                            rs.getString("zipcode"),
                            rs.getDouble("latitude"),
                            rs.getDouble("longitude"),
                            rs.getFloat("star_rating"),
                            rs.getInt("num_tips"),
                            0, //assign rank to 0. rank field is needed for similarity search query result.
                            0.0 //assign distance to 0. distance field is needed for similarity search query result.
                    );
                }
            }
        } catch (SQLException ex) {
            logger.severe("Business details query failed!: " + ex.getMessage());
        }
        try {
            connection.close();
        } catch (SQLException e) {
            e.printStackTrace();
        }
        return res;
    }

    public List<String> getBusinessCategories(String business_id) {
        List<String> categories = new ArrayList<>();

        String query = """
            SELECT categoryname
            FROM business_category
            WHERE businessid = ?
            ORDER BY categoryname
            """;

        try {
            connection = DriverManager.getConnection(JDBC_URL, JDBC_USER, JDBC_PASS);
        } catch (SQLException ex) {
            ex.printStackTrace();
        }

        try (PreparedStatement ps = connection.prepareStatement(query)) {
            ps.setString(1, business_id);
            ResultSet rs = ps.executeQuery();
            while (rs.next()) {
                categories.add(rs.getString("categoryname"));
            }
        } catch (SQLException ex) {
            logger.severe("Business categories query failed!: " + ex.getMessage());
        }

        try {
            connection.close();
        } catch (SQLException e) {
            e.printStackTrace();
        }
        return categories;
    }

    public List<Map<String, String>> getBusinessAttributes(String business_id) {
        List<Map<String, String>> attributes = new ArrayList<>();

        String query = """
            SELECT attributename, value
            FROM business_attribute
            WHERE businessid = ?
            ORDER BY attributename
            """;

        try {
            connection = DriverManager.getConnection(JDBC_URL, JDBC_USER, JDBC_PASS);
        } catch (SQLException ex) {
            ex.printStackTrace();
        }

        try (PreparedStatement ps = connection.prepareStatement(query)) {
            ps.setString(1, business_id);
            ResultSet rs = ps.executeQuery();
            while (rs.next()) {
                Map<String, String> attribute = new HashMap<>();
                attribute.put("attribute_name", rs.getString("attributename"));
                attribute.put("value", rs.getString("value"));
                attributes.add(attribute);
            }
        } catch (SQLException ex) {
            logger.severe("Business attributes query failed!: " + ex.getMessage());
        }

        try {
            connection.close();
        } catch (SQLException e) {
            e.printStackTrace();
        }
        return attributes;
    }

    public Map<String, String> getTodaySchedule(String business_id) {
        Map<String, String> schedule = new HashMap<>();
        schedule.put("day", "");
        schedule.put("open", "");
        schedule.put("close", "");

        String query = """
            SELECT TRIM(day) AS day, open, close
            FROM schedule
            WHERE businessid = ?
            AND TRIM(day) = TRIM(TO_CHAR(CURRENT_DATE, 'Day'))
            """;

        try {
            connection = DriverManager.getConnection(JDBC_URL, JDBC_USER, JDBC_PASS);
        } catch (SQLException ex) {
            ex.printStackTrace();
        }

        try (PreparedStatement ps = connection.prepareStatement(query)) {
            ps.setString(1, business_id);
            ResultSet rs = ps.executeQuery();
            if (rs.next()) {
                schedule.put("day", rs.getString("day"));
                schedule.put("open", rs.getString("open"));
                schedule.put("close", rs.getString("close"));
            }
        } catch (SQLException ex) {
            logger.severe("Business schedule query failed!: " + ex.getMessage());
        }

        try {
            connection.close();
        } catch (SQLException e) {
            e.printStackTrace();
        }
        return schedule;
    }

    public List<Business> getSimilarBusinesses(String business_id) {
        List<Business> businesses = new ArrayList<>();

        String query = """
            SELECT b2.businessid AS business_id, b2.name AS business_name,
                   b2.streetaddress AS street_address, b2.city, b2.state,
                   b2.zip AS zipcode, b2.latitude, b2.longitude,
                   b2.stars AS star_rating, b2.num_tips,
                   count_categories(b1.businessid, b2.businessid) AS rank,
                   geodistance(b1.latitude, b1.longitude, b2.latitude, b2.longitude) AS distance
            FROM business b1, business b2
            WHERE b1.businessid = ?
              AND b1.businessid <> b2.businessid
              AND b1.zip = b2.zip
              AND geodistance(b1.latitude, b1.longitude, b2.latitude, b2.longitude) <= 20
              AND count_categories(b1.businessid, b2.businessid) > 0
            ORDER BY rank DESC, distance ASC
            LIMIT 20
            """;

        try {
            connection = DriverManager.getConnection(JDBC_URL, JDBC_USER, JDBC_PASS);
        } catch (SQLException ex) {
            ex.printStackTrace();
        }

        try (PreparedStatement ps = connection.prepareStatement(query)) {
            ps.setString(1, business_id);
            ResultSet rs = ps.executeQuery();
            while (rs.next()) {
                businesses.add(new Business(
                        rs.getString("business_id"),
                        rs.getString("business_name"),
                        rs.getString("street_address"),
                        rs.getString("city"),
                        rs.getString("state"),
                        rs.getString("zipcode"),
                        rs.getDouble("latitude"),
                        rs.getDouble("longitude"),
                        rs.getFloat("star_rating"),
                        rs.getInt("num_tips"),
                        rs.getInt("rank"),
                        rs.getDouble("distance")
                ));
            }
        } catch (SQLException ex) {
            logger.severe("Similar businesses query failed!: " + ex.getMessage());
        }

        try {
            connection.close();
        } catch (SQLException e) {
            e.printStackTrace();
        }
        return businesses;
    }


    public List<String> queryCities(String state) {
        List<String> cities = new ArrayList<>();
        logger.info("queryCities called");
        if (state == null) {
            return cities;
        }
        String categoryQuery = """
            SELECT DISTINCT b.City
            FROM business b
            WHERE b.state = ?
            ORDER BY b.City""";

        try {
            connection = DriverManager.getConnection(JDBC_URL,JDBC_USER, JDBC_PASS );
        } catch (SQLException ex) {
            ex.printStackTrace();
        }

        try (PreparedStatement ps = connection.prepareStatement(categoryQuery)){
            logger.info("Executing query: " + categoryQuery);
            ps.setString(1, state); //fills the ? parameter
            ResultSet rs = ps.executeQuery();
            while (rs.next()) {
                cities.add(rs.getString("City"));
            }
        } catch (SQLException ex) {
            logger.severe("Error executing query: " + ex.getMessage());
            ex.printStackTrace();
        }
        try {
            connection.close();
        } catch (SQLException e) {
            e.printStackTrace();
        }

        return cities;
    }
    public Map<String, List<String>> queryWiFiPriceRange(String state, String city) {
        List<String> wifi = new ArrayList<>();
        List<String> priceRange = new ArrayList<>();
        logger.info("queryWiFiPriceRange");

        String query = """
            SELECT DISTINCT b.attributename, b.value
            FROM business_attribute b
            JOIN business ON business.businessid = b.businessid
            WHERE business.state = ? AND business.city = ?
            AND b.attributename IN ('WiFi', 'RestaurantsPriceRange2')
            ORDER BY b.attributename, b.value""";

        try {
            connection = DriverManager.getConnection(JDBC_URL,JDBC_USER, JDBC_PASS );
        } catch (SQLException ex) {
            ex.printStackTrace();
        }

        try (PreparedStatement ps = connection.prepareStatement(query)){
            logger.info("Executing query: " + query);
            ps.setString(1, state); //fills the ? parameter
            ps.setString(2, city); //fills the ? parameter
            ResultSet rs = ps.executeQuery();
            while (rs.next()) {
                String attrName = rs.getString("attributename");
                String value = rs.getString("value");
                if (attrName.equals("WiFi")){
                    wifi.add(value);
                }else if (attrName.equals("RestaurantsPriceRange2")){
                    priceRange.add(value);
                }
            }
        } catch (SQLException ex) {
            logger.severe("Error executing query: " + ex.getMessage());
            ex.printStackTrace();
        }
        try {
            connection.close();
        } catch (SQLException e) {
            e.printStackTrace();
        }
        Map<String, List<String>> result = new HashMap<>();
        result.put("wifi", wifi);
        result.put("priceRange", priceRange);
        return result;
    }
        }
