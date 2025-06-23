-- manually adding sources
INSERT INTO work_scraper.sources (website)
VALUES ('cvvp.nva.gov.lv')
ON CONFLICT DO NOTHING;