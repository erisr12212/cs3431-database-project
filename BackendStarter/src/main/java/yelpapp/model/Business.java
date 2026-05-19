package yelpapp.model;

public class Business {
    private final String business_name;
    private final String street_address;
    private final String city;
    private final String state;
    private final String zipcode;
    private final String business_id;
    private final double latitude;
    private final double longitude;
    private final int num_tips;
    private final float star_rating;
    private int rank = 0;
    private double distance;

    public Business(String business_id,
                    String name,
                    String address,
                    String city,
                    String state,
                    String zipcode,
                    double latitude,
                    double longitude,
                    float star_rating,
                    int tipCount,
                    int rank,
                    double distance) {
        this.business_id = business_id;
        this.business_name = name;
        this.street_address = address;
        this.city = city;
        this.state = state;
        this.zipcode = zipcode;
        this.latitude = latitude;
        this.longitude = longitude;
        this.star_rating = star_rating;
        this.num_tips = tipCount;
        this.rank = rank;
        this.distance = distance;
    }
    public String getBusiness_id() {
        return business_id;
    }

    public String getBusiness_name() {
        return business_name;
    }

    public String getStreet_address() {
        return street_address;
    }

    public String getCity() { return city; }
    public String getState() { return state; }
    public String getZipcode() { return zipcode; }

    public float getStar_rating() {
        return star_rating;
    }

    public int getNum_tips() {
        return num_tips;
    }

    public int getRank() { return rank; }

    public Double getLatitude() { return latitude; }
    public Double getLongitude() { return longitude; }
    public double getDistance() { return distance; }
}
